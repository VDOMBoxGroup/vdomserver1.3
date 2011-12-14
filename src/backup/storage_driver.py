from subprocess import *
import shlex
import managers
import utils.uuid
from utils.system import get_external_drives, device_exists, mount_device, umount_device

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
		self.name = "Cloud iSCSI Drive"
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
		except:
			raise Exception("Can't get data from Smartcard %s %s"%(self.__cloud_login, self.__cloud_pass))

		try:
		# Get share status

			cmd = """sh /opt/boot/mount_iscsi.sh -Gs -l %s -p %s """%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# state: ok
				self.__cloud_share_status = 0

			elif rc == 1:
			# state: empty
				self.__cloud_share_status = 1
				debug("To be activated! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))

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
				debug("Crap! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))
		except:
			pass

		if self.__cloud_share_status != 1:
		# Get and Install openvpn configs
			debug("Try to get configs! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))
			cmd = """sh /opt/boot/mount_iscsi.sh -Gc -l %s -p %s """%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Got configs 
				self.__cloud_configs = 1
				debug("Configs got %s ! Login: %s Pass: %s"%(self.__cloud_configs, self.__cloud_login, self.__cloud_pass))
			else:
				raise Exception("Crap! %s %s"%(self.__cloud_login, self.__cloud_pass))
		else:
			raise Exception("Crap! Stop! ")



		if self.__cloud_configs == 1:
		# Configs exist. Now: Connect
			cmd = """sh /opt/boot/mount_iscsi.sh -C """
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Connected. Now scan for targets.
				cmd = """sh /opt/boot/mount_iscsi.sh -S """
				out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
				out.wait()
				rc = out.returncode

				if rc == 0:
				# Got targets. Login.
					self.__cloud_target = str(out.stdout.read()).strip('\n')

					cmd = """sh /opt/boot/mount_iscsi.sh -Li -t %s """%(self.__cloud_target)
					out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
					out.wait()
					rc = out.returncode

					if rc == 0:
					# Logged in. Probe
						self.__dev = str(out.stdout.read()).strip('\n')

						cmd = """sh /opt/boot/mount_iscsi.sh -P -d %s"""%self.__dev
						out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
						out.wait()
						rc = out.returncode

						if rc == 0:
						# mount
							self.__uuid = str(out.stdout.read()).strip('\n')

							cmd = """sh /opt/boot/mount_iscsi.sh -M -u %s """%(self.__uuid)
							out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
							out.wait()
							rc = out.returncode

							if rc == 0:
							# Mounted ok, nothing to do. Umount
								self.__path = str(out.stdout.read()).strip('\n')

								cmd = """sh /opt/boot/mount_iscsi.sh -U -u %s """%(self.__uuid)
								out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
								out.wait()
								rc = out.returncode

								if rc == 0:
								# Umount OK. All OK! Now - logout from target.
									debug("iSCSI %s Logout ."%self.__cloud_target )
									
									cmd = """sh /opt/boot/mount_iscsi.sh -Lo -t %s """%(self.__cloud_target )
									out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
									out.wait()
									rc = out.returncode
									
									if rc == 0:
										debug("Logged out from %s " % self.__cloud_target )
									else:
										raise Exception("Ololo pwpw")
								else:
								# Umount wrong. Try to reinit or just forget.
									debug("iSCSI - Smth wrong on UMOUNT")
						else:
							# Mount wrong! Exit.
							debug("iSCSI MOUNT %s %s failed! Exit."%(self.__dev, self.__uuid))
							raise Exception("iSCSI MOUNT failed! Exit.")
					else:
					# Login to target failed. Exit.
						debug("iSCSI Login to target failed! Exit.")
						raise Exception("iSCSI Login to target %s failed! Exit."%self.__cloud_target )
				else:
				# No such targets. Exit
					debug("iSCSI targets not found! Exit.")
					raise Exception("iSCSI targets not found! Exit.")
			else:
			# Can't connect openvpn.
				debug("iSCSI cannot connect ovpn! Exit.")
				raise Exception("iSCSI ovpn failed! Exit.")


		else:
		# No such configs. Nothing to do.
			debug("iSCSI No such configs. Nothing to do. Exit.")
			raise Exception("iSCSI No such configs. Nothing to do. Exit.")

	def mount(self):
		try:
		# Get share status

			cmd = """sh /opt/boot/mount_iscsi.sh -Gs -l %s -p %s """%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# state: ok
				self.__cloud_share_status = 0

			elif rc == 1:
			# state: empty
				self.__cloud_share_status = 1
				debug("To be activated! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))

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
				raise Exception("Crap! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))
		except Exception as e:
			raise Exception(str(e))

		if self.__cloud_share_status != 1:
		# Get and Install openvpn configs
			debug("Try to get configs! Login: %s Pass: %s"%(self.__cloud_login, self.__cloud_pass))
			cmd = """sh /opt/boot/mount_iscsi.sh -Gc -l %s -p %s """%(self.__cloud_login, self.__cloud_pass)
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Got configs 
				self.__cloud_configs = 1
				debug("Configs got %s ! Login: %s Pass: %s"%(self.__cloud_configs, self.__cloud_login, self.__cloud_pass))
			else:
				raise Exception("Crap! %s %s"%(self.__cloud_login, self.__cloud_pass))
		else:
			raise Exception("Crap! Stop! ")



		if self.__cloud_configs == 1:
		# Configs exist. Now: Connect
			cmd = """sh /opt/boot/mount_iscsi.sh -C """
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode

			if rc == 0:
			# Connected. Now scan for targets.
				cmd = """sh /opt/boot/mount_iscsi.sh -S """
				out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
				out.wait()
				rc = out.returncode

				if rc == 0:
				# Got targets. Login.
					self.__cloud_target = str(out.stdout.read()).strip('\n')

					cmd = """sh /opt/boot/mount_iscsi.sh -Li -t %s """%(self.__cloud_target)
					out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
					out.wait()
					rc = out.returncode

					if rc == 0:
					# Logged in. Probe
						self.__dev = str(out.stdout.read()).strip('\n')

						cmd = """sh /opt/boot/mount_iscsi.sh -P -d %s"""%self.__dev
						out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
						out.wait()
						rc = out.returncode

						if rc == 0:
						# mount
							self.__uuid = str(out.stdout.read()).strip('\n')

							cmd = """sh /opt/boot/mount_iscsi.sh -M -u %s """%(self.__uuid)
							out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
							out.wait()
							rc = out.returncode

							if rc == 0:
							# Mounted ok, nothing to do. Umount
								self.__path = str(out.stdout.read()).strip('\n')
								cmd = """sh /opt/boot/mount_iscsi.sh -D """
								out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
								out.wait()
								rc = out.returncode
								
								if rc == 0:
									debug("OVPN disconnected." )
									debug("--------")
									debug("SELF.__PATH = %s"%self.__path)
									debug("--------")
									return self.__path
								else:
									debug("OVPN dicsonnect failed.")
									return False
							else:
								debug("iSCSI Mount failed.")
								return False
						else:
							# Probe wrong! Exit.
							debug("iSCSI Probe dev: %s  uuid: %s failed! Exit."%(self.__dev, self.__uuid))
							raise Exception("iSCSI MOUNT failed! Exit.")
					else:
					# Login to target failed. Exit.
						debug("iSCSI Login to target failed! Exit.")
						raise Exception("iSCSI Login to target %s failed! Exit."%self.__cloud_target )
				else:
				# No such targets. Exit
					debug("iSCSI targets not found! Exit.")
					raise Exception("iSCSI targets not found! Exit.")
			else:
			# Can't connect openvpn.
				debug("iSCSI cannot connect ovpn! Exit.")
				raise Exception("iSCSI ovpn failed! Exit.")


		else:
		# No such configs. Nothing to do.
			debug("iSCSI No such configs. Nothing to do. Exit.")
			raise Exception("iSCSI No such configs. Nothing to do. Exit.")


	def umount(self):
		debug("-- Umount start \n UUID: %s  DEV: %s PATH: %s"%(self.__uuid, self.__dev, self.__path))
		cmd = """sh /opt/boot/mount_iscsi.sh -U -u %s """%(self.__uuid)
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode

		if rc == 0:
			debug("-- Umount OK! \n UUID: %s  DEV: %s PATH: %s"%(self.__uuid, self.__dev, self.__path))
			cmd = """sh /opt/boot/mount_iscsi.sh -Lo -t %s """%(self.__cloud_target )
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			
			if rc == 0:
				debug("Logged out from %s " % self.__cloud_target )
				
				cmd = """sh /opt/boot/mount_iscsi.sh -D """
				out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
				out.wait()
				rc = out.returncode
				
				if rc == 0:
					debug("OVPN disconnected OK!" )
					return True
				else:
					debug("OVPN disconnect FAILED!" )
					return False
			else:
				raise Exception("LOGOUT FROM TARGET FAILED! pwpwpw")
		else:
			debug("Can't umount %s in %s"%(self.__dev, self.__path))
			return False

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

backup_storage_manager = VDOM_backup_storage_manager()