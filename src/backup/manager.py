import managers, version
from scheduler.task import VDOM_backup_task
from storage_driver import backup_storage_manager
from backup import backup


class VDOM_backup_manager(object):
    
    def __init__(self):
        backup_storage_manager.restore()
        
    def backup(self, app_id, drv_id):
        appl = managers.xml_manager.get_application(app_id)
        sd = backup_storage_manager.get_driver(drv_id)
        path = sd.path
        meta_info = appl.info_map
        server_version = version.VDOM_server_version
        vh = managers.request_manager.current.server().virtual_hosting()
        sites = vh.get_sites()
        vhosts = []
        for site in sites:
            if vh.get_site(site) == app_id:
                vhosts.append(site)
                
        backup.backup(app_id, path, meta_info, server_version, vhosts)
    
    def get_schedule(self, driver_id):
        schedule_list = managers.scheduler_manager.fetch(VDOM_backup_task)
        schedule = []
        for key in schedule_list:
            if schedule_list[key][0].driver == driver_id:
                schedule.append(schedule_list[key])
        if schedule and len(schedule) == 1:
            return schedule[0]
        else:
            return None
        
    def add_schedule(self, driver_id, app_list, interval, rotation):
        schedule = VDOM_backup_task(driver_id, app_list, rotation)
        return managers.scheduler_manager.add_task(schedule, interval)
    
    def update_schedule(self, driver_id, app_list, interval, rotation):
        schedule_list = managers.scheduler_manager.fetch(VDOM_backup_task)
        for key in schedule_list:
            if driver.id == schedule_list[key][0].driver:
                schedule_list[key][0].applications = app_list
                schedule_list[key][0].rotation = rotation
                managers.scheduler_manager.update(key, schedule_list[key][0], interval)
        
    def del_schedule(self, task_id):
        managers.scheduler_manager.dell_task(task_id)
    
    def get_storages(self):
        return backup_storage_manager.get_drivers()
    
    def add_storages(self, driver):
        backup_storage_manager.add_driver(driver)
        
    def del_storage(self, driver):
        backup_storage_manager.del_driver(driver)
        schedule_list = managers.scheduler_manager.fetch(VDOM_backup_task)
        remove_list = []
        is_dirty_index = False
        for key in schedule_list:
            if driver.id == schedule_list[key][0].driver:
                remove_list.append(key)
                is_dirty_index = True
        if is_dirty_index:
            for key in remove_list:
                managers.scheduler_manager.dell_task(key)
                
    
    def get_revision_list(self):
        pass
    