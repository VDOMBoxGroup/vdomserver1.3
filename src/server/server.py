"""VDOM HTTP server module"""

import os, thread

from version import VDOM_server_version
from utils.server import VDOM_server, VDOM_thread
from http_server import VDOM_http_server
from request_handler import VDOM_http_request_handler


class VDOM_http_server_thread(VDOM_thread):

	def __init__(self):
		VDOM_thread.__init__(self, name="HTTP Server")

	def main(self):
		server_address = (VDOM_CONFIG["SERVER-ADDRESS"], VDOM_CONFIG["SERVER-PORT"])
		self.__server = VDOM_http_server(server_address, VDOM_http_request_handler)
		debug(VDOM_http_request_handler.server_version + " listening on port " + str(VDOM_CONFIG["SERVER-PORT"]))
		self.__server.daemon_threads=True
		self.__server.serve_forever()

	def stop(self):
		self.__server.shutdown()

class VDOM_box_server(VDOM_server):
	"""VDOM server class"""

	def prepare(self):
		VDOM_http_server_thread().start()
