
from utils.threads import VDOM_server as VDOM_base_server
from web import VDOM_web_server_thread


class VDOM_server(VDOM_base_server):

	def prepare(self):
		VDOM_web_server_thread().start()
