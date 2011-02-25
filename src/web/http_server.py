"""VDOM http server module"""

import sys, os
import posixpath
import urllib
import shutil
import mimetypes
import re
import socket
import select
import thread
import time
import random
import traceback
import SocketServer, BaseHTTPServer, SimpleHTTPServer, SOAPpy

import managers
import log
from utils.pid import VDOM_server_pid
from utils.exception import VDOM_exception
from utils.semaphore import VDOM_semaphore

from vhosting import VDOM_vhosting
from soap.functions import *
#from local_server import execute
#from local_server import send_to_card
from soap.wsdl import gen_wsdl
from soap.wsdl import methods as wsdl_methods

rexp = re.compile(r"vr0\:.+inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL)
rexp2 = re.compile(r"eth0.+inet addr\:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL)
class VDOM_http_server(SocketServer.ThreadingTCPServer):
	"""VDOM threading http server class"""

	def __init__(self, server_address, request_handler_class):
		"""constructor"""
		self.__server_address = server_address
		self.__current_connections = 0
		self.__stop = False
		self.restart = False

		sys.stderr.write(_("WSDL file available at %s\n" % VDOM_CONFIG["WSDL-FILE-URL"]))

		# initialize random generator
		random.seed()

		# initialize virtual hosting
		self.__vhosting = VDOM_vhosting()

		#drop pid to file
		self.__pidfile = VDOM_CONFIG["SERVER-PIDFILE"]
		if self.__pidfile != "":
			VDOM_server_pid(self.__pidfile)

		# init SOAP
		encoding = 'UTF-8'
		# Test the encoding, raising an exception if it's not known
		if encoding != None:
			''.encode(encoding)
		config = SOAPpy.Config
		self.config = config

		# soap debug options
		self.config.debug = 0
		self.config.VDOM_debug = 0
		self.config.dumpSOAPIn = 0
		self.config.dumpSOAPOut = 0
		self.config.dumpHeadersIn = 0
		self.config.dumpHeadersOut = 0

		self.config.buildWithNamespacePrefix = False

		ssl_context = None
		if ssl_context != None and not config.SSLserver:
			raise AttributeError, "SSL server not supported by this Python installation"
		namespace = "http://services.vdom.net/VDOMServices"
		log = 0
		self.namespace          = namespace
		self.objmap             = {}
		self.funcmap            = {}
		self.ssl_context        = ssl_context
		self.encoding           = encoding
		self.log                = log
		self.allow_reuse_address= 1

		#call base class constructor
		SocketServer.TCPServer.__init__(self, server_address, request_handler_class)

		#create semaphore
		self.__sem = VDOM_semaphore()

		# register soap methods
		for method in wsdl_methods.keys():
			exec("""self.registerFunction(SOAPpy.MethodSig(%s, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")""" % method)
#		self.registerFunction(SOAPpy.MethodSig(login, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")
#		self.registerFunction(SOAPpy.MethodSig(create_application, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")
#		self.registerFunction(SOAPpy.MethodSig(set_application_info, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")

		# generate wsdl file
		gen_wsdl()
		#send_to_card("online")

	def __del__(self):
		"""destructor, remove pid file"""
		VDOM_server_pid(self.__pidfile, False, True)

	def get_request(self):
		"""get the request and client address from the socket"""
		while True:
			ret = select.select([self.socket], [], [])
			for r in ret[0]:
				if r == self.socket:
					sock, addr = self.socket.accept()
					if self.ssl_context:
						sock = SSL.Connection(self.ssl_context, sock)
						sock._setup_ssl(addr)
						if sock.accept_ssl() != 1:
							raise socket.error, "Couldn't accept SSL connection"
					return sock, addr

	def current_connections(self):
		"""access current_connections property"""
		return self.__current_connections

#	def access_log(self):
#		"""get access log"""
#		return self.__access_log

#	def error_log(self):
#		"""get error log"""
#		return self.__error_log

	def virtual_hosting(self):
		"""get virtual hosting"""
		return self.__vhosting

	def server_address(self):
		"""access server address"""
		return self.__server_address

	def serve_forever(self):
		"""handle each request in separate thread"""
		# while not self.__stop:
		#	self.handle_request()
		SocketServer.ThreadingTCPServer.serve_forever(self)
		idx = 0
		while self.__current_connections and idx < 30:
			time.sleep(0.1)
			idx += 1

	def verify_request(self, request, client_address):
		"""verify the request by matching client address with the stored regexp"""
		self.__deny = 0
		return True

	def finish_request(self, request, client_address):
		"""finish one request by instantiating RequestHandlerClass"""
		self.__sem.lock()
		card = True
		limit = True
		#if system_options.get("object_amount", "") is "":
		#	pass#card = False
		#else:
		#	l = 0
		#	try: l = int(system_options["object_amount"])
		#	except: pass
		#	if "1" != system_options["server_license_type"] and l < managers.xml_manager.obj_count:
		#		limit = False
		self.__reject = 0
#		if self.__current_connections >= self.__maximum_connections: self.__reject = 1
#		else:
		self.__current_connections += 1
		self.client_address = client_address
		if "127.0.0.1" != client_address[0]:
			debug("Increase: %d (from %s:%d)" % (self.__current_connections, client_address[0], client_address[1]))
		self.__sem.unlock()
		try:
			self.RequestHandlerClass(request, client_address, self, {"reject":self.__reject, "deny":self.__deny, "card":card, "limit":limit, "connections":self.__current_connections})
		except Exception, e:
			do_handle = True
			if isinstance(e, socket.error):
				do_handle = False
			if self.__current_connections > 0:
				self.__current_connections -= 1
				if "127.0.0.1" != client_address[0]:
					debug("Decrease: %d" % self.__current_connections)
					#import gc
					#debug("\nGarbage: "+str(len(gc.garbage))+"\n", "vdomsvr")
					#if len(gc.garbage) > 0:
					#	print str(gc.garbage)
			if do_handle:
				self.handle_error(request, client_address)

	def notify_finish(self, client_address):
		"""must be called by the handler to notify the server about the end of the request processing"""
		self.__sem.lock()
		if self.__current_connections > 0:
			self.__current_connections -= 1
			if "127.0.0.1" != client_address[0]:
				debug("Decrease: %d" % self.__current_connections)
				#import gc
				#debug("\nGarbage: "+str(len(gc.garbage))+"\n", "vdomsvr")
				#if len(gc.garbage) > 0:
				#	print str(gc.garbage)
		self.__sem.unlock()

	def get_cur_con(self):
		return self.__current_connections

	def get_wsdl(self):
		"""get wsdl data"""
		# !!! TODO: cache wsdl
		ff = open(VDOM_CONFIG["WSDL-FILE-LOCATION"], "rb")
		data = ff.read()
		ff.close()
		return data

	def handle_error(self, request, client_address):
		"""handle an error"""
		#self.__error_logger.error("VDOM_http_server", os.getpid(), "Exception happened during processing of request from \"%s\"", client_address)
		fe = "".join(['-'*40, "Exception happened during processing of request from ", 
			str(client_address), traceback.format_exc(), '-'*40])
		debug(fe)

	# soap handler registration methods
	def registerObject(self, object, namespace = '', path = ''):
		if namespace == '' and path == '': namespace = self.namespace
		if namespace == '' and path != '':
			namespace = path.replace("/", ":")
			if namespace[0] == ":": namespace = namespace[1:]
		self.objmap[namespace] = object

	def registerFunction(self, function, namespace = '', funcName = None, path = ''):
		if not funcName : funcName = function.__name__
		if namespace == '' and path == '': namespace = self.namespace
		if namespace == '' and path != '':
			namespace = path.replace("/", ":")
			if namespace[0] == ":": namespace = namespace[1:]
		if namespace in self.funcmap:
			self.funcmap[namespace][funcName] = function
		else:
			self.funcmap[namespace] = {funcName : function}

	def registerKWObject(self, object, namespace = '', path = ''):
		if namespace == '' and path == '': namespace = self.namespace
		if namespace == '' and path != '':
			namespace = path.replace("/", ":")
			if namespace[0] == ":": namespace = namespace[1:]
		for i in dir(object.__class__):
			if i[0] != "_" and callable(getattr(object, i)):
				self.registerKWFunction(getattr(object,i), namespace)

	# convenience  - wraps your func for you.
	def registerKWFunction(self, function, namespace = '', funcName = None, path = ''):
		if namespace == '' and path == '': namespace = self.namespace
		if namespace == '' and path != '':
			namespace = path.replace("/", ":")
			if namespace[0] == ":": namespace = namespace[1:]
		self.registerFunction(MethodSig(function,keywords=1), namespace, funcName)

	def unregisterObject(self, object, namespace = '', path = ''):
		if namespace == '' and path == '': namespace = self.namespace
		if namespace == '' and path != '':
			namespace = path.replace("/", ":")
			if namespace[0] == ":": namespace = namespace[1:]

		del self.objmap[namespace]
