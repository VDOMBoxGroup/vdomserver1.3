
from utils.threads import VDOM_server as VDOM_threads_server
#from storage import VDOM_storage_writer
#from file_access import VDOM_file_manager_writer
#from memory import VDOM_xml_synchronizer
from watcher import VDOM_watcher
from local_server import VDOM_local_server_thread
from web import VDOM_web_server_thread,VDOM_secure_web_server_thread



class VDOM_server(VDOM_threads_server):

	def prepare(self):
		#self.__storage_writer=VDOM_storage_writer()
		#self.__storage_writer.start()
		#self.__file_manager_writer=VDOM_file_manager_writer()
		#self.__file_manager_writer.start()
		#self.__xml_synchronizer=VDOM_xml_synchronizer()
		#self.__xml_synchronizer.start()

		self.__watcher_thread=VDOM_watcher()
		self.__watcher_thread.start()

		self.__local_server_thread=VDOM_local_server_thread()
		self.__local_server_thread.start()
		
		self.__web_server_thread=VDOM_web_server_thread()
		self.__web_server_thread.start()
		
		self.__secure_web_server_thread=VDOM_secure_web_server_thread()
		self.__secure_web_server_thread.start()		
		
		#self.__webdav_server_thread=VDOM_webdav_server_thread()
		#self.__webdav_server_thread.start()


	def stop_secure_server(self):
		self.__secure_web_server_thread.stop()
		
	def start_secure_server(self):
		self.__secure_web_server_thread=VDOM_secure_web_server_thread()
		self.__secure_web_server_thread.start()