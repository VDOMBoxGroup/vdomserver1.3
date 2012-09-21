
import sys, os, thread

from version import VDOM_server_version
from utils.threads import VDOM_thread
from http_server import VDOM_http_server
from http_request_handler import VDOM_http_request_handler
import managers

class VDOM_web_server_thread(VDOM_thread):

	def __init__(self):
		VDOM_thread.__init__(self, name="Web Server")
		self.__server=None

	def main(self):
		sys.stderr.write("Start %s\n"%self.name)
		server_address=(VDOM_CONFIG["SERVER-ADDRESS"], VDOM_CONFIG["SERVER-PORT"])
		self.__server=VDOM_http_server(server_address, VDOM_http_request_handler, use_ssl = False)

		msg = "%s listening on port %s"%(VDOM_http_request_handler.server_version, VDOM_CONFIG["SERVER-PORT"])
		print (msg)
		managers.log_manager.info_server(msg, "Web server thread")
		self.__server.daemon_threads=True
		self.__server.serve_forever()

	def stop(self):
		sys.stderr.write("Stop %s\n"%self.name)
		if self.__server: self.__server.shutdown()
