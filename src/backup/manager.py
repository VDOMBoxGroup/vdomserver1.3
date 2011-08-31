import backup, restore, storage_driver, scheduler, managers, version


class VDOM_backup_manager(object):
    
    def __init__(self):
        self._backup = backup.VDOM_backup()
        self._restore = restore.VDOM_restore()
        self.backup_storage_manager = storage_driver.VDOM_backup_storage_manager()
        self._scheduler = scheduler.VDOM_scheduler_manger()
    def backup(self, app_id, path):
        appl = managers.xml_manager.get_application(app_id)
        meta_info = appl.info_map
        server_version = version.VDOM_server_version
        vh = managers.request_manager.current.server().virtual_hosting()
        sites = vh.get_sites()
        vhosts = []
        for site in sites:
            if vh.get_site(site) == app_id:
                vhosts.append(site)
                
        self._backup.backup(app_id, path, meta_info, server_version, vhosts)
    def restore(self, app_id, meta_info, server_version, vhost="default"):
        pass
    def get_schedule(self, driver_id):
        tasks = self._scheduler.get_tasks()
        return tasks[driver_id]
    def add_schedule(self, driver_id, app_list, interval, rotation):
        self._scheduler.get_task(driver_id, app_list, interval, rotation)
    def get_storages(self):
        return self.backup_storage_manager.get_drivers()
    def add_storages(self, driver):
        self.backup_storage_manager.add_driver(driver)
    def get_revision_list(self):
        pass
    