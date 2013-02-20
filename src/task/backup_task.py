import managers
from task import VDOM_task
from status import VDOM_task_status

class VDOM_backup_task(VDOM_task):

	def get_status(self):
		
		return self.status
	
	def start(self):
		
		self.status.progress = 0
		self.status.message = "proccessing backup"
		
	def stop(self):
		
		self.status.progress = 100
		self.status.message = "backup has finished"