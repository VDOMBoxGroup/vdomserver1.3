import managers
import utils.uuid

class VDOM_storage_driver(object):
    
    def __init__(self):
        self.id = str(utils.uuid.uuid4())
    
    def mount(self):
        pass
    
    def umount(self):
        pass
    
    
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