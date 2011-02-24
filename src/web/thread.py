
import os, thread

from version import VDOM_server_version
from server import VDOM_thread
from http_server import VDOM_http_server
from request_handler import VDOM_http_request_handler


class VDOM_http_server_thread(VDOM_thread):

	def __init__(self):
		VDOM_thread.__init__(self, name="HTTP Server")
		self.__server=None

	def main(self):
		server_address=(VDOM_CONFIG["SERVER-ADDRESS"], VDOM_CONFIG["SERVER-PORT"])
		self.__server=VDOM_http_server(server_address, VDOM_http_request_handler)
		debug("%s listening on port %s"%(VDOM_http_request_handler.server_version, VDOM_CONFIG["SERVER-PORT"]))
		self.__server.daemon_threads=True
		self.__server.serve_forever()

	def stop(self):
		if self.__server: self.__server.shutdown()
