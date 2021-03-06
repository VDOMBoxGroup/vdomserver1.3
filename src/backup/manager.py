import managers, os, utils.uuid
from scheduler.task import VDOM_scheduled_backup
from storage_driver import backup_storage_manager
from backup import backup
from restore import VDOM_restore
from task import VDOM_backup_task, VDOM_restore_task


class VDOM_backup_manager(object):

	def __init__(self):
		backup_storage_manager.restore()

	def backup(self, app_id, drv_id, rotation, taskid=None):
		task = VDOM_backup_task()
		task.id = taskid
		if taskid: managers.task_manager.add_task(task)
		task.start()
		try:
			sd = backup_storage_manager.get_driver(drv_id)
			path = sd.mount()
			if not path:
				debug("Storage driver is not mounted")
				return
			no_encryption = 1 if sd.type == "local_folder" else 0
			result = backup.backup(app_id, path, rotation, no_encryption)
			sd.umount()
			task.stop()
			stat = task.get_status()		
			if result[0] != 0:
				stat.progress = -1
			stat.message = str(result[1])
			return result
		except Exception, e:
			task.stop()
			stat = task.get_status()
			stat.progress = -1
			stat.message = unicode(e)
			return (1, unicode(e))

	def get_schedule(self, driver_id):
		schedule_list = managers.scheduler_manager.fetch(VDOM_scheduled_backup)
		schedule = []
		for key in schedule_list:
			if schedule_list[key][0].driver == driver_id:
				schedule.append((key, schedule_list[key]))
		if schedule and len(schedule) == 1:
			return schedule[0]
		else:
			return None

	def get_schedule_list(self):
		return managers.scheduler_manager.fetch(VDOM_scheduled_backup)

	def add_schedule(self, driver_id, app_list, interval, rotation):
		schedule = VDOM_scheduled_backup(driver_id, app_list, rotation)
		return managers.scheduler_manager.add_task(schedule, interval)

	def update_schedule(self, driver_id, app_list, interval, rotation):
		schedule_list = managers.scheduler_manager.fetch(VDOM_scheduled_backup)
		schedule = []
		for key in schedule_list:
			if driver_id == schedule_list[key][0].driver:
				schedule_list[key][0].applications = app_list
				schedule_list[key][0].rotation = rotation
				schedule.append([key, schedule_list[key][0]])
		if len(schedule) == 1:
			return managers.scheduler_manager.update(schedule[0][0], schedule[0][1], interval)
		else: return False


	def del_schedule(self, driver_id):
		schedule_list = managers.scheduler_manager.fetch(VDOM_scheduled_backup)
		schedule = []
		is_dirty_index = False
		for key in schedule_list:
			if schedule_list[key][0].driver == driver_id:
				schedule.append(key)
				is_dirty_index = True
		if is_dirty_index and schedule and len(schedule) == 1:
			managers.scheduler_manager.dell_task(schedule[0])

	def get_storages(self):
		drivers = backup_storage_manager.get_drivers()
		if drivers:
			return drivers
		else:
			return dict()

	def get_storage(self, drv_id):
		return backup_storage_manager.get_driver(drv_id)

	def add_storage(self, driver):
		backup_storage_manager.add_driver(driver)

	def del_storage(self, driver):
		backup_storage_manager.del_driver(driver)
		schedule_list = managers.scheduler_manager.fetch(VDOM_scheduled_backup)
		remove_list = []
		is_dirty_index = False
		for key in schedule_list:
			if driver.id == schedule_list[key][0].driver:
				remove_list.append(key)
				is_dirty_index = True
		if is_dirty_index:
			for key in remove_list:
				managers.scheduler_manager.dell_task(key)


	def get_app_list(self, driver_id):
		driver = backup_storage_manager.get_driver(driver_id)
		driver_path = driver.mount()
		app_list = VDOM_restore().list_apps(driver_path)
		driver.umount()
		return app_list

	def get_revision_list(self, driver_id, app_id):
		driver = backup_storage_manager.get_driver(driver_id)
		driver_path = driver.mount()
		revisions_list = VDOM_restore().revisions(driver_path, app_id)
		driver.umount()
		return revisions_list

	def get_revision_info(self, driver_id, app_id, rev_num):
		driver = backup_storage_manager.get_driver(driver_id)
		driver_path = driver.mount()
		revision_info = VDOM_restore().revision_info(driver_path, app_id, rev_num)
		driver.umount()
		return revision_info

	def restore(self, driver_id, app_id, revision_number, taskid=None):
		task = VDOM_restore_task()
		task.id = taskid
		if taskid: managers.task_manager.add_task(task)
		task.start()
		try:
			driver = backup_storage_manager.get_driver(driver_id)
			no_encryption = 1 if driver.type == "local_folder" else 0
			ret = VDOM_restore().restore(driver, app_id, revision_number, no_encryption)
			task.stop()
			stat = task.get_status()		
			if ret[0]:
				stat.message = str(revision_number)
			else:
				stat.progress = -1
				stat.message = ret[1]
			return ret
		except Exception, e:
			task.stop()
			stat = task.get_status()
			stat.progress = -1
			stat.message = unicode(e)
			return (False, unicode(e))			
