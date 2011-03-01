
import sys
from utils.threads import VDOM_daemon


class VDOM_storage_writer(VDOM_daemon):
	
	name="Storage Writer"

	def __init__(self, manager):
		VDOM_daemon.__init__(self, name=VDOM_storage_writer.name)
		self.__manager=manager

	def prepare(self):
		sys.stderr.write("Start %s\n"%self.name)
		self.__connection,  self.__cursor=self.__manager.prepare()

	def cleanup(self):
		sys.stderr.write("Stop %s\n"%self.name)
		self.__manager.work(self.__connection, self.__cursor)

	def work(self):
		self.__manager.work(self.__connection, self.__cursor)
