import managers
from task import VDOM_task
from status import VDOM_task_status

class VDOM_restore_task(VDOM_task):

	def get_status(self):
		
		return self.status
	
	def start(self):
		
		self.status.progress = 0
		self.status.message = "restoring..."
		
	def stop(self):
		
		self.status.progress = 100
		self.status.message = "restore has finished"