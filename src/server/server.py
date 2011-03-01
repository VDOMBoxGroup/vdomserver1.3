
from utils.threads import VDOM_server as VDOM_threads_server
from memory import VDOM_xml_sync_daemon
from web import VDOM_web_server_thread


class VDOM_server(VDOM_threads_server):

	def prepare(self):
		VDOM_xml_sync_daemon().start()
		VDOM_web_server_thread().start()
