from subprocess import *
import shlex
import managers
import utils.uuid
from utils.system import get_external_drives, device_exists, mount_device, umount_device
from os import path, mkdir

class VDOM_storage_driver(object):

	def __init__(self):
		self.id = str(utils.uuid.uuid4())
		
	@staticmethod
	def get_sd_size(mount_point):
		cmd = """sh /opt/boot/get_disksize.sh -s -m %s"""%mount_point
		try:
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
				size = str(out.stdout.read()).strip('\n')
		except:
			size = "0"

		cmd = """sh /opt/boot/get_disksize.sh -u -m %s"""%mount_point
		try:
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
				used = str(out.stdout.read()).strip('\n')
		except:
			used = "0"

		cmd = """sh /opt/boot/get_disksize.sh -f -m %s"""%mount_point
		try:
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
				free = str(out.stdout.read()).strip('\n')
		except:
			free = "0"

		cmd = """sh /opt/boot/get_disksize.sh -p -m %s"""%mount_point
		try:
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
				percent = str(out.stdout.read()).strip('\n')
		except:
			percent = "0%"


		return(size, used, free, percent) # (size, used, free, percent)

	def mount(self):
		pass

	def umount(self):
		pass

class VDOM_sd_external_drive(VDOM_storage_driver):

	def __init__(self, dev, crypt=False):
		self.id = str(utils.uuid.uuid4())
		self.name = "External Drive"
		self.type = "external_drive"
		self.__path = None
		self.__dev = dev
		self.__uuid = None
		self.crypt = crypt

		
		try:
			cmd = """sh /opt/boot/mount_and_get_path.sh -p -d %s"""%dev
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
				self.__uuid = str(out.stdout.read()).strip('\n')
			
			cmd = """sh /opt/boot/mount_and_get_path.sh -n -d %s"""%dev
			
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
				self.name = str(out.stdout.read()).strip('\n')
		except:
			pass


	@staticmethod
	def get_device_list():
		cmd = """sh /opt/boot/mount_and_get_path.sh -s"""
		devs = []
		try:
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
				devs = str(out.stdout.read())
				devs = [tuple(devs.split(";")) for devs in devs.strip().split("\n")] if devs else []
				return devs
			else:
				return devs
		except:
			return devs


	def change_device(self, dev):
		if dev != self.__dev:
			try:
				self.__dev = dev
				cmd = """sh /opt/boot/mount_and_get_path.sh -p -d %s"""%dev
				out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
				out.wait()
				rc = out.returncode
	
				if rc == 0:
					self.__uuid = str(out.stdout.read()).strip('\n')
				else: 
					return False
				cmd = """sh /opt/boot/mount_and_get_path.sh -n -d %s"""%dev
				
				out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
				out.wait()
				rc = out.returncode
	
				if rc == 0:
					self.name = str(out.stdout.read()).strip('\n')
				else: 
					return False
			
			except:
				return False
				return True
		else:
			return False

	def erase_storage(self):
		try:
			debug("let us remove everything from %s"%self.__path)
			self.mount()
			cmd = """sh /opt/boot/erase_storage.sh -p %s"""%(self.__path)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				debug("Erasing of %s successfully completed."%(self.__path))
				return True
			else:
				debug("Erasing of %s totally failed!"%(self.__path))
				return False
		except Exception,e :
			debug("Erasing failed: %s", e)

			
	def mount(self):
		debug("MOUNT")
		# SEARCH for not mounted drives
		cmd = """sh /opt/boot/mount_and_get_path.sh -m -D %s"""%self.__uuid
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode

		if rc == 0:
			debug("MOUNT OK")
			self.__path = str(out.stdout.read()).strip('\n')
			return self.__path
		elif rc == 1:
			debug("MOUNT FAILED")
			return False

	def umount(self):
		debug("UMOUNT")
		cmd = """sh /opt/boot/mount_and_get_path.sh -D %s -u"""%self.__uuid
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode
		if rc == 0:
			return True
		else:
			return str(out.stderr.read())
		
	dev = property(lambda self: self.__dev)
	
class VDOM_cloud_storage_driver(VDOM_storage_driver):
	def __init__(self, crypt=False):
		self.id = str(utils.uuid.uuid4())
		self.name = "Cloud Drive"
		self.type = "cloud_drive"
		self.crypt = crypt
		self.__path = None
		self.__dev = None
		self.__uuid = None
		self.__cloud_login = None
		self.__cloud_pass = None
		self.__cloud_share_status = None
		self.__cloud_configs = None
		self.__cloud_target = None


		try:
		# Get login/pass for cloud

			from utils.card_connect import send_to_card_and_wait
			result = send_to_card_and_wait("getlicense %s %s" % ("0", "106"),"%s/%s" % ("0", "106"))
			self.__cloud_login = result
			#if result == "None":
				# no such field in license
				#return int(result) if result not in [None, "None"] else 0
			#	debug("Can't get login from Smartcard")
			#	raise Exception("Can't get login from Smartcard")
			#else:
			#	self.__cloud_login = result

			result = send_to_card_and_wait("getlicense %s %s" % ("0", "107"),"%s/%s" % ("0", "107"))
			self.__cloud_pass = result
			#if result == "None":
				# no such field in license
				#return int(result) if result not in [None, "None"] else 0
			#	debug("Can't get password from Smartcard")
			#	raise Exception("Can't get pass from Smartcard")
			#else:
			#	self.__cloud_pass = result
			
			if self.crypt:
				crypto_arg = "--crypto --crypto-pass %s"%(self.__cloud_pass)
			else:
				crypto_arg = ""
			

		except:
			raise Exception("Can't get data from Smartcard %s "%(self.__cloud_login))

		try:
		# Get share status

			cmd = """sh /opt/boot/mount_sshfs.sh -Gs -l %s -p %s %s"""%(self.__cloud_login, self.__cloud_pass, crypto_arg)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# state: ok
				self.__cloud_share_status = 0

			elif rc == 1:
			# state: empty
				self.__cloud_share_status = 1
				debug("To be activated! Login: %s Pass: %s "%(self.__cloud_login, self.__cloud_pass))

			elif rc == 2: 
			# state: extended
				self.__cloud_share_status = 2
				debug("Extended! Need in extention. Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))

			elif rc == 3:
			# state: reduced
				self.__cloud_share_status = 3
				debug("Reduced! Need in reinit. Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))

			else:
				self.__cloud_share_status = 10
				debug("Unknown status of space! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))
		except:
			pass

		if self.__cloud_share_status != 1:
		# Write password to Cloud
			debug("Try to write password to Cloud! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))
			cmd = """sh /opt/boot/mount_sshfs.sh -Gc -l %s -p %s """%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Password inserted
				self.__cloud_configs = 1
				debug("Password inserted %s ! Login: %s Pass: %s"%(self.__cloud_configs, self.__cloud_login, self.__cloud_pass))
			else:
				raise Exception("Can't get configs for Cloud. Check something. Login: %s "%(self.__cloud_login))
		else:
			raise Exception("Space is not active! Stop! Login: %s "%(self.__cloud_login))



		if self.__cloud_configs == 1:
		# Pasword presented. Now: Mount
			cmd = """sh /opt/boot/mount_sshfs.sh -M -l %s  -p %s"""%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Mounted ok, nothing to do. Umount
				self.__path = str(out.stdout.read()).strip('\n')
				debug("Mounted %s with %s "%(self.__path, self.__cloud_login))

				cmd = """sh /opt/boot/mount_sshfs.sh -U -m %s """%(self.__path)
				out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
				out.wait()
				rc = out.returncode

				if rc == 0:
				# Umount OK. All OK! Now - logout from target.
					debug("Umounted %s ."%self.__path )
				else:
				# Umount wrong! Exit.
					debug("UMOUNT %s failed! Exit."%(self.__path))
					raise Exception("UMOUNT %s failed! Exit."%(self.__path))

			else:
			# Mount failed. Exit.
				debug("MOUNT %s failed! Exit."%(self.__cloud_login))
				raise Exception("Mount %s failed! Exit."%self.__cloud_login)
		else:
		# No such configs. Nothing to do.
			debug("There is no presented password. Nothing to do. Exit.")
			raise Exception("There is no presented password. Nothing to do. Exit.")

	def erase_storage(self):
		try:
			debug("let us remove everything from %s"%self.__path)
			self.mount()
			cmd = """sh /opt/boot/erase_storage.sh -p %s"""%(self.__path)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				debug("Erasing of %s successfully completed."%(self.__path))
				return True
			else:
				debug("Erasing of %s totally failed!"%(self.__path))
				return False
		except Exception,e :
			debug("Erasing failed: %s", e)

	def mount(self):

		try:
		# Get share status

			cmd = """sh /opt/boot/mount_sshfs.sh -Gs -l %s -p %s %s"""%(self.__cloud_login, self.__cloud_pass, crypto_arg)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# state: ok
				self.__cloud_share_status = 0

			elif rc == 1:
			# state: empty
				self.__cloud_share_status = 1
				debug("To be activated! Login: %s Pass: %s "%(self.__cloud_login, self.__cloud_pass))

			elif rc == 2: 
			# state: extended
				self.__cloud_share_status = 2
				debug("Extended! Need in extention. Login: %s "%(self.__cloud_login))

			elif rc == 3:
			# state: reduced
				self.__cloud_share_status = 3
				debug("Reduced! Need in reinit. Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))

			else:
				self.__cloud_share_status = 10
				debug("Unknown status of space! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))
		except:
			pass

		if self.__cloud_share_status != 1:
		# Write password to Cloud
			debug("Try to write password to Cloud! Login: %s "%(self.__cloud_login))
			cmd = """sh /opt/boot/mount_sshfs.sh -Gc -l %s -p %s """%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Password inserted
				self.__cloud_configs = 1
				debug("Password inserted %s ! Login: %s Pass: %s"%(self.__cloud_configs, self.__cloud_login, self.__cloud_pass))
			else:
				raise Exception("Can't get configs for Cloud. Check something. Login: %s "%(self.__cloud_login))
		else:
			raise Exception("Space is not active! Stop! Login: %s "%(self.__cloud_login))



		if self.__cloud_configs == 1:
		# Pasword presented. Now: Mount
			cmd = """sh /opt/boot/mount_sshfs.sh -M -l %s  -p %s"""%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Mounted ok, nothing to do. Umount
				self.__path = str(out.stdout.read()).strip('\n')
				debug("Mounted %s"%(self.__path))
				return self.__path

			else:
			# Mount failed. Exit.
				debug("MOUNT %s failed! Exit."%(self.__path))
				raise Exception("Mount %s failed! Exit."%self.__cloud_login)
		else:
		# No such configs. Nothing to do.
			debug("There is no presented password. Nothing to do. Exit.")
			raise Exception("There is no presented password. Nothing to do. Exit.")
			

	def umount(self):
		debug("-- Umount start \n PATH: %s"%(self.__path))
		cmd = """sh /opt/boot/mount_sshfs.sh -U -m %s """%(self.__path)
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode

		if rc == 0:
			debug("-- Umount OK! \n PATH: %s"%(self.__path))
			return True
		else:
			debug("Umount %s failed! Login: %s "%(self.__path, self.__cloud_login))
			return False

class VDOM_smb_storage_driver(VDOM_storage_driver):
	def __init__(self, crypt=False):
		self.id = str(utils.uuid.uuid4())
		self.name = "Windows Share"
		self.type = "smb_drive"
		self.crypt = crypt
		self.__path = None
		self.__dev = None
		self.__uuid = None
		self.__smb_login = None
		self.__smb_pass = None
		self.__smb_host = None
		self.__smb_location = None

	def authentificate(self, login, password, host, location):
		try:
			cmd = """sh /opt/boot/mount_samba.sh -c -l %s -p %s -h %s -L %s"""%(login, password, host, location)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				debug("SMB test connection to %s OK."%(host))
				self.__smb_host = host
				self.__smb_login = login
				self.__smb_pass = password
				self.__smb_location = location
				
				return True
			else:
				debug("SMB test connection to %s under %s %s FAILED!"%(host, login, password))
				return False
		except Exception as e :
			debug("SMB connection failed: %s" % str(e))


	def erase_storage(self):
		try:
			debug("let us remove everything from %s"%self.__path)
			self.mount()
			cmd = """sh /opt/boot/erase_storage.sh -p %s"""%(self.__path)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				debug("Erasing of %s successfully completed."%(self.__path))
				return True
			else:
				debug("Erasing of %s totally failed!"%(self.__path))
				return False
		except Exception as e :
			debug("Erasing failed: %s", str(e))

	def mount(self):
		try:
			cmd = """sh /opt/boot/mount_samba.sh -m -h %s -l %s -p %s -L %s"""%(self.__smb_host, self.__smb_login, self.__smb_pass, self.__smb_location)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				self.__path = str(out.stdout.read()).strip('\n')
				debug("Mounted %s"%(self.__path))
				return self.__path
			else:
				debug("SMB mount to %s under %s %s FAILED!"%(self.__smb_host, self.__smb_login, self.__smb_pass))
				return False
		except Exception as e :
			debug("SMB mount failed: %s" % str(e))		

	def umount(self):
		try:
			cmd = """sh /opt/boot/mount_samba.sh -u -p %s"""%(self.__path)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				debug("SMB umount in %s OK."%(self.__path))
				return True
			else:
				debug("SMB umount %s FAILED!"%(self.__path))
				return False
		except Exception as e :
			debug("SMB umount failed: %s", str(e))
			
	login=property(lambda self: self.__smb_login)
	password=property(lambda self: self.__smb_pass)
	host=property(lambda self: self.__smb_host)
	location=property(lambda self: self.__smb_location)

class VDOM_backup_storage_manager(object):

	def __init__(self):
		self.__index = {}

	def restore(self):
		self.__index = managers.storage.read_object(VDOM_CONFIG["BACKUP-STORAGE-DRIVER-INDEX-RECORD"])
		if not self.__index:
			self.__index = {}

	def add_driver(self, driver):
		"""add new driver"""
		self.__index[driver.id] = driver
		managers.storage.write_object_async(VDOM_CONFIG["BACKUP-STORAGE-DRIVER-INDEX-RECORD"], self.__index)

	def del_driver(self, driver):
		"""delete driver"""
		if driver.id not in self.__index:
			pass
		else:
			self.__index.pop(driver.id)
			managers.storage.write_object_async(VDOM_CONFIG["BACKUP-STORAGE-DRIVER-INDEX-RECORD"], self.__index)

	def get_drivers(self):
		return self.__index

	def get_driver(self, id):
		if id in self.__index:
			return self.__index[id]
		else:
			return None


class VDOM_local_folder_drive(VDOM_storage_driver):

	def __init__(self, crypt=False):
		self.id = str(utils.uuid.uuid4())
		self.name = "Local Folder driver"
		self.type = "local_folder"
		self.__path = None
		self.__uuid = None
		self.crypt = crypt
		
		# Check folder to be exist
		debug("LOCAL BACKUP: check %s for existing"%self.__path)
		self.__path = "/var/vdom/local_backup/"
		if not path.isdir(self.__path):
			mkdir(self.__path)
		

	def erase_storage(self):
		try:
			debug("let us remove everything from %s"%self.__path)
			self.mount()
			cmd = """sh /opt/boot/erase_storage.sh -p %s"""%(self.__path)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				debug("Erasing of %s successfully completed."%(self.__path))
				return True
			else:
				debug("Erasing of %s totally failed!"%(self.__path))
				return False
		except Exception,e :
			debug("Erasing failed: %s", e)

			
	def mount(self):
		debug("LOCAL BACKUP: mount..")
		# SEARCH for not mounted drives
		if not path.isdir(self.__path):
			mkdir(self.__path)
			debug("LOCAL BACKUP: mount %s OK"%self.__path)
			return self.__path
		else:
			debug("LOCAL BACKUP: mount %s OK"%self.__path)
			return self.__path
		
	def umount(self):
		debug("LOCAL BACKUP: umount %s OK"%self.__path)	
		return True



backup_storage_manager = VDOM_backup_storage_manager()



##
## 12345
## fake