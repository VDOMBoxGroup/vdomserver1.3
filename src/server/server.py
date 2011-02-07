"""VDOM HTTP server module"""

import os, thread

from src.version import VDOM_server_version
from http_server import VDOM_http_server
from request_handler import VDOM_http_request_handler
from vdommem_socket_server import VDOM_memory_socket_server
from vdommem_request_handler import VDOM_memory_request_handler

class VDOM_server:
	"""VDOM server class"""

	def start(self):
		"""start server"""
		thread.start_new_thread(self.vdom_memory_server, ())
		server_address = (VDOM_CONFIG["SERVER-ADDRESS"], VDOM_CONFIG["SERVER-PORT"])
		self.server = VDOM_http_server(server_address, VDOM_http_request_handler)
		debug(VDOM_http_request_handler.server_version + " listening on port " + str(VDOM_CONFIG["SERVER-PORT"]))
		self.server.serve_forever()

	def vdom_memory_server(self):
		server_address = ('localhost', VDOM_CONFIG["VDOM-MEMORY-SERVER-PORT"])
		server = VDOM_memory_socket_server(server_address, VDOM_memory_request_handler)
		debug("VDOM memory server listening on port " + str(VDOM_CONFIG["VDOM-MEMORY-SERVER-PORT"]))
		server.serve_forever()
