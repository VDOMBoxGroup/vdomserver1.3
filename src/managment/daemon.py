
import sys
from utils.threads import VDOM_daemon


class VDOM_backup(VDOM_daemon):
	
	name="Backup"

	def __init__(self, manager):
		VDOM_daemon.__init__(self, name=VDOM_backup.name)
		self.__manager=manager

	def prepare(self):
		sys.stderr.write("Start %s\n"%self.name)
		self.__t1=self.__manager.prepare()

	def cleanup(self):
		sys.stderr.write("Stop %s\n"%self.name)
		self.__manager.work(self.__t1)

	def work(self):
		self.__manager.work(self.__t1)
