import managers
import utils.uuid
from subprocess import *
import shlex

class VDOM_storage_driver(object):
    
    def __init__(self):
        self.id = str(utils.uuid.uuid4())
    
    def mount(self):
        pass
    
    def umount(self):
        pass

class VDOM_sd_external_drive(VDOM_storage_driver):

    def __init__(self):
        self.id = str(utils.uuid.uuid4())
        self.name = "External Drive for backup %s"%(self.id)
        self.__path = None
        self.ololo= "gogogo"
    
    def mount(self):
		# SEARCH for not mounted drives
		cmd = """sh /opt/boot/mount_and_get_path.sh -s"""
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode

		if rc == 0:
			drives = out.stdout.read()
			cmd = """sh /opt/boot/mount_and_get_path.sh -d %s -m"""%drivers
			out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
			out.wait()
			rc = out.returncode
			if rc == 0:
				self.__path = out.stdout.read()
				return self.__path
			else:
				return False
		elif rc == 1:
			return False
		
    
    def umount(self):
		cmd = """sh /opt/boot/mount_and_get_path.sh -d %s -u"""%self.__path
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode
		if rc == 0:
			return True
		else:
			return False

class VDOM_backup_storage_manager(object):
    
    def __init__(self):
        self.__index = {}
    
    def restore(self):
        self.__index = managers.storage.read_object(VDOM_CONFIG["BACKUP-STORAGE-DRIVER-INDEX-RECORD"])
        
    def add_driver(self, driver):
        """add new driver"""
        if driver.id in self.__index:
            pass
        else:
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

backup_storage_manager = VDOM_backup_storage_manager()