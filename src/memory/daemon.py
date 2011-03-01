
import sys
from utils.threads import VDOM_daemon
from file_access import VDOM_file_manager_writer

class VDOM_xml_synchronizer(VDOM_daemon):
	
	name="XML Synchronizer"
	
	def __init__(self, manager):
		VDOM_daemon.__init__(self, name=VDOM_xml_synchronizer.name,
			sleep=VDOM_CONFIG["APP-SAVE-TIMEOUT"],
			dependencies=VDOM_file_manager_writer.name)
		self.__manager=manager

	def prepare(self):
		sys.stderr.write("Start %s\n"%self.name)

	def cleanup(self):
		sys.stderr.write("Stop %s\n"%self.name)
		self.__manager.work()

	def work(self):
		self.__manager.work()
    