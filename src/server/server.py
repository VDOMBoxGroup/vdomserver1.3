
from utils.threads import VDOM_server as VDOM_threads_server
#from storage import VDOM_storage_writer
#from file_access import VDOM_file_manager_writer
#from memory import VDOM_xml_synchronizer
from web import VDOM_web_server_thread


class VDOM_server(VDOM_threads_server):

	def prepare(self):
		#self.__storage_writer=VDOM_storage_writer()
		#self.__storage_writer.start()
		#self.__file_manager_writer=VDOM_file_manager_writer()
		#self.__file_manager_writer.start()
		#self.__xml_synchronizer=VDOM_xml_synchronizer()
		#self.__xml_synchronizer.start()
		
		self.__web_server_thread=VDOM_web_server_thread()
		self.__web_server_thread.start()
