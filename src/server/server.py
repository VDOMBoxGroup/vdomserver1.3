"""VDOM HTTP server module"""

import os, thread

from version import VDOM_server_version
from http_server import VDOM_http_server
from request_handler import VDOM_http_request_handler

class VDOM_server:
	"""VDOM server class"""

	def start(self):
		"""start server"""
		server_address = (VDOM_CONFIG["SERVER-ADDRESS"], VDOM_CONFIG["SERVER-PORT"])
		self.server = VDOM_http_server(server_address, VDOM_http_request_handler)
		debug(VDOM_http_request_handler.server_version + " listening on port " + str(VDOM_CONFIG["SERVER-PORT"]))
		self.server.serve_forever()
