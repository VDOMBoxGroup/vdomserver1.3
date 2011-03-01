
import sys
from utils.threads import VDOM_daemon


class VDOM_file_manager_writer(VDOM_daemon):
	
	name="File Manager Writer"

	def __init__(self, manager):
		VDOM_daemon.__init__(self, name=VDOM_file_manager_writer.name)
		self.__manager=manager

	def prepare(self):
		sys.stderr.write("Start %s\n"%self.name)

	def cleanup(self):
		sys.stderr.write("Stop %s\n"%self.name)
		self.__manager.work()

	def work(self):
		self.__manager.work()
