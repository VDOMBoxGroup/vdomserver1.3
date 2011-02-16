"""VDOM memory socket server module"""

import sys, os, posixpath, urllib, shutil, mimetypes, socket, select, thread, time, random, traceback
import SocketServer, BaseHTTPServer, SimpleHTTPServer

from util.exception import *
from util.semaphore import VDOM_semaphore


class VDOM_memory_socket_server(SocketServer.ThreadingTCPServer):
	"""VDOM memory threading socket server class"""

	def __init__(self, server_address, request_handler_class):
		"""constructor"""
		self.server_address = server_address
		self.current_connections = 0
		self.allow_reuse_address = 1
		#create semaphore
		self.__sem = VDOM_semaphore()
		#call base class constructor
		SocketServer.TCPServer.__init__(self, server_address, request_handler_class)

	def get_request(self): # DUPLICATE METHOD
		"""get the request and client address from the socket"""
		sock, addr = self.socket.accept()
		return sock, addr

	def serve_forever(self):
		"""handle each request in separate thread"""
		while True:
			self.handle_request()

	def verify_request(self, request, client_address): # DUPLICATE METHOD
		return True

	def finish_request(self, request, client_address):
		"""finish one request by instantiating RequestHandlerClass"""
		self.__sem.lock()
		self.current_connections += 1
		debug("Increase: %d" % self.current_connections, "vdommem")
		self.__sem.unlock()
		try:
			self.RequestHandlerClass(request, client_address, self)
		except Exception, e:
			do_handle = True
			if isinstance(e, socket.error):
				do_handle = False
			if self.current_connections > 0:
				self.current_connections -= 1
				debug("Decrease: %d" % self.current_connections, "vdommem")
				import gc
				debug("\nGarbage: "+str(len(gc.garbage))+"\n", "vdommem")
			if do_handle:
				self.handle_error(request, client_address)

	def notify_finish(self):
		"""must be called by the handler to notify the server about the end of the request processing"""
		self.__sem.lock()
		if self.current_connections > 0:
			self.current_connections -= 1
			debug("Decrease: %d" % self.current_connections, "vdommem")
			import gc
			debug("\nGarbage: "+str(len(gc.garbage))+"\n", "vdommem")
		self.__sem.unlock()

	def handle_error(self, request, client_address):
		"""handle an error"""
		fe = "".join(['-'*40, "Exception happened during processing of request from ", 
			str(client_address), traceback.format_exc(), '-'*40])
		debug(fe, "vdommem")
