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
        return(None, None, None, None) # (size, used, free, percent)

    def mount(self):
        pass

    def umount(self):
        pass

class VDOM_sd_external_drive(VDOM_storage_driver):

    def __init__(self, dev):
        self.id = str(utils.uuid.uuid4())
        self.name = "External Drive"
        self.type = "external_drive"
        self.__path = None
        self.__dev = dev
        self.__uuid = None

        cmd = """sh /opt/boot/mount_and_get_path.sh -p -d %s"""%dev
        try:
            out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
            out.wait()
            rc = out.returncode

            if rc == 0:
                self.__uuid = str(out.stdout.read()).strip('\n')
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
                return devs.strip().split("\n")
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
                    return True
            except:
                return False
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