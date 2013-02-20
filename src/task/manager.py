import managers

class VDOM_task_manager():

	def __init__(self):
		
		self.__tasks = {}

	def get_status(self, task_id):

		task = self.__tasks.get(task_id, None)
		stat = task.get_status() if task else None
		if stat:
			return stat
		return

	def get_task_list(self):

		return self.__tasks

	def add_task(self, task_object):

		self.__tasks[task_object.id] = task_object

	def del_task(self, task_id):

		self.__tasks.pop(task_id)

	def stop_task(self, task_id):

		task = self.__tasks.get(task_id, None)
		if task:
			task.stop()
