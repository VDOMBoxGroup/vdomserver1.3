import thread, os, time, tempfile, shutil

import managers, log
from utils.semaphore import VDOM_semaphore
from utils.exception import VDOM_exception
from utils.system import *
from utils.app_management import import_application

class VDOM_server_manager():

	def __init__(self):
		self.__sem = VDOM_semaphore()
		# backup options
		self.backup_app = []
		self.history = 0
		self.interval = 0	# minutes
		self.backup_type = "zip"
		self.backup_dev = ""
		self.conf = managers.storage.read_object(VDOM_CONFIG["BACKUP-STORAGE-RECORD"])
		if self.conf:
			self.history = self.conf.get("history", 0)
			self.interval = self.conf.get("interval", 0)
			self.backup_dev = self.conf.get("backup_dev", "")
			b = self.conf.get("backup_app", [])
			for i in b:
				try:
					managers.xml_manager.get_application(i)
					self.backup_app.append(i)
				except:
					pass
		else:
			self.conf = {}
		# thread
		thread.start_new_thread(self.__backup_thread, ())

	def save_conf(self):
		self.conf["history"] = self.history
		self.conf["interval"] = self.interval
		self.conf["backup_app"] = self.backup_app
		self.conf["backup_dev"] = self.backup_dev
		managers.storage.write_object_async(VDOM_CONFIG["BACKUP-STORAGE-RECORD"], self.conf)

	def configure_backup(self, applist = [], hist = 0, interv = 0, dev = ""):
		self.__sem.lock()
		for a in applist:
			if a not in self.backup_app:
				self.backup_app.append(a)
		if hist > 0:
			self.history = hist
		if interv > 0:
			self.interval = interv
		self.backup_dev = dev
		self.save_conf()
		self.__sem.unlock()

	def cancel_backup(self, applist = []):
		self.__sem.lock()
		for a in applist:
			if a in self.backup_app:
				self.backup_app.remove(a)
		if 0 == len(applist):
			self.backup_app = []
		self.history = 0
		self.interval = 0
		self.backup_dev = ""
		self.save_conf()
		self.__sem.unlock()

	def __backup_thread(self):
		t1 = time.time()
		while True:
			if len(self.backup_app) > 0 and self.history > 0 and self.interval > 0:
				t2 = time.time()
				if t2 - t1 >= 60 * self.interval:
					basedir = VDOM_CONFIG["BACKUP-DIRECTORY"]
					if self.backup_dev and device_exists(self.backup_dev):
						mountpoint = mount_device(self.backup_dev)
						basedir = os.path.join(mountpoint, "vdombackup")
						try: os.makedirs(basedir)
						except: pass
						if not os.path.isdir(basedir):
							t1 = time.time()
							umount_device(self.backup_dev)
							managers.log_manager.error_server("can't create path '%s'" % basedir, caller="backup")
							continue
					self.__sem.lock()
					#
					for a in self.backup_app:
						try: managers.xml_manager.get_application(a)
						except: continue
						direct = os.path.join(basedir, a)
						try: os.makedirs(direct)
						except: pass
						if not os.path.isdir(direct):
							managers.log_manager.error_server("can't create path '%s'" % direct, caller="backup")
							continue
						managers.xml_manager.export_application(a, self.backup_type, direct)
						self.__do_backup(direct, a)
					#
					self.__sem.unlock()
					if self.backup_dev and device_exists(self.backup_dev):
						umount_device(self.backup_dev)
					t1 = time.time()
			else:
				t1 = time.time()
			time.sleep(60)

	def __do_backup(self, direct, app_id):
		this_name = app_id + "." + self.backup_type
		l = os.listdir(direct)
		l.remove(this_name)
		l.sort()
		while len(l) >= self.history:
			os.remove(os.path.join(direct, l.pop()))
		k = len(l)
		for i in xrange(k):
			try: os.remove(os.path.join(direct, app_id + "_" + str(k - i) + "." + self.backup_type))
			except: pass
			try: os.rename(os.path.join(direct, l[k - i - 1]), os.path.join(direct, app_id + "_" + str(k - i) + "." + self.backup_type))
			except: pass
		try: os.rename(os.path.join(direct, this_name), os.path.join(direct, app_id + "_0." + self.backup_type))
		except: pass

		
	def sharebackup(self, dev = ""):
		self.vfs_backup_dev = dev
		#thread.start_new_thread(self.__sharebackup_thread, ())
		self.__sharebackup_thread()
		
		
	def __sharebackup_thread(self):
		f = os.popen("/bin/sh /opt/boot/vfs_backup.sh %s"%(self.vfs_backup_dev))
		outp = f.read()
		f.close()


	def sharerestore(self, dev = ""):
		self.vfs_restore_dev = dev
		#thread.start_new_thread(self.__sharerestore_thread, ())
		self.__sharerestore_thread()
		
	def __sharerestore_thread(self):
		f = os.popen("/bin/sh /opt/boot/vfs_backup.sh -r %s"%(self.vfs_restore_dev))
		outp = f.read()
		f.close()

	def export_application_to_usb(self, dev, application):
		pass
		
	def restore_application(self, appid, file):
		if os.path.split(file)[1].split("_")[0] != appid:
			raise VDOM_exception(_("Application ID doesn't match to the file"))
		# uninstall application
		try:
			managers.xml_manager.uninstall_application(appid)
			debug("Application '%s' has been removed" % appid)
		except: pass
		tmpfilename = tempfile.mkstemp("." + file.split(".")[-1].lower(), "", VDOM_CONFIG["TEMP-DIRECTORY"])
		os.close(tmpfilename[0])
		tmpfilename = tmpfilename[1]
		shutil.copyfile(file, tmpfilename)
		import_application(tmpfilename)
		os.remove(tmpfilename)


internal_mngr = VDOM_server_manager()
del VDOM_server_manager
