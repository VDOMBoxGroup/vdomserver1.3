import managers
import utils.uuid

class VDOM_scheduler(object):
    
    def __init__(self):
        self.id = str(utils.uuid.uuid4())
        self.driver_id = ""
        self.app_list = []
        self.interval  = 0
        self.rotation = 0
        
class VDOM_scheduler_manger(object):

    def __init__(self):
        self.__index = managers.storage.read_object(VDOM_CONFIG["BACKUP-SCHEDULER-INDEX-STORAGE-RECORD"])
    
    def add_task(self, drv_id, app_list, interval, rotation):
        task = VDOM_scheduler()
        task.driver_id = drv_id
        task.app_list = app_list
        task.interval = interval
        task.rotation = rotation
        self.__index[task.driver_id] = task
        self.save_task()
        self.build_crontab(task.driver_id, task.interval)
    
    def get_tasks(self, drv_id):
        return self.__index
    
    def save_task(self):
        managers.storage.write_object_async(VDOM_CONFIG["BACKUP-SCHEDULER-INDEX-STORAGE-RECORD"], self.__index)
        
    def dell_task(self, drv_id):
        if drv_id not in self.__index:
            pass
        else:
            self.__index.pop(drv_id)
            self.save_task()
            
    def build_crontab(self, driver_id, interval):
        pass
    