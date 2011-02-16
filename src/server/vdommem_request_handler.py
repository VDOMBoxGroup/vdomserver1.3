"""vdom memory server request handler module"""

import sys, os, posixpath, urllib, shutil, mimetypes, thread, re, socket, select, threading, time, SocketServer, traceback, zlib
from cStringIO import StringIO

from vdommem_scripts import *
import managers

#class BaseRequestHandler:
#
#    def __init__(self, request, client_address, server):
#        self.request = request
#        self.client_address = client_address
#        self.server = server
#        try:
#            self.setup()
#            self.handle()
#            self.finish()
#        finally:
#            sys.exc_traceback = None    # Help garbage collection
#
#    def setup(self):
#        pass
#
#    def handle(self):
#        pass
#
#    def finish(self):
#        pass

#class StreamRequestHandler(BaseRequestHandler):
#
#    rbufsize = -1
#    wbufsize = 0
#
#    def setup(self):
#        self.connection = self.request
#        self.rfile = self.connection.makefile('rb', self.rbufsize)
#        self.wfile = self.connection.makefile('wb', self.wbufsize)
#
#    def finish(self):
#        if not self.wfile.closed:
#            self.wfile.flush()
#        self.wfile.close()
#        self.rfile.close()


class VDOM_memory_request_handler(SocketServer.StreamRequestHandler):
	"""VDOM memory request handler"""

	def finish(self):
		"""finish processing request"""
		SocketServer.StreamRequestHandler.finish(self)
		"""tell the server that processing is finished"""
		self.server.notify_finish()

	def handle(self):
		"""handle request"""
		self.__app = None
		while True:
			some = self.get_request_data()
			if not some:
				break
			method_name, params, err = self.parse_request(some)
			if not method_name or params is None:
				self.send_error(err)
			else:
				debug("handle vdom memory request '%s'" % method_name, "vdommem")
				if hasattr(self, method_name):
					try:
						x = getattr(self, method_name)(params)
						if x:
							self.send_response(x)
						else:
							self.send_response("None")
					except Exception, e:
						traceback.print_exc(file=debugfile)
						self.send_error(str(e))
				else:
					self.send_response("None")
		if self.__app:
			self.__app.release()

	def send_response(self, some):
		self.wfile.write(some)
		self.wfile.flush()

	def send_error(self, err):
		self.wfile.write("<Error>%s</Error>" % err)
		self.wfile.flush()

	def get_request_data(self):
		resp = ""
		ret = select.select([self.connection], [], [])
		if len(ret[0]) > 0:
			while True:
				resp += self.connection.recv(4096)
				if "close" == resp:
					return None
				ret = select.select([self.connection], [], [], 0)
				if len(ret[0]) == 0:
					break
		return resp

	def parse_request(self, data):		# return (method_name, params, err)
		o = None
		try:
			o = xml_object(srcdata = data)
			if "method" != o.lname:
				raise ValueError
			method_name = o.attributes["name"].lower()
			param = {}
			for c in o.children:
				if "parameter" != c.lname:
					raise ValueError
				param[c.attributes["name"].lower()] = c.value
			o.delete()
			return (method_name, param, None)
		except:
			#traceback.print_exc(file=debugfile)
			#debug(data)
			if o:
				o.delete()
			return (None, None, "Incorrect request format")

	# --------------------------------------------------------------------------

	def open_session(self, params):
		appid = params["appid"]
		write = int(params["write"])
		self.__app = managers.xml_manager.get_application(appid)
		if write:
			try:
				self.__app.lock_write()
			except VDOM_exception_restart():
				return "<Restart></Restart>"
		else:
			self.__app.lock_read()

	# --- vdom memory ----------------------------------------------------------

	def get_application(self, params):
		appid = params["appid"]
		x = managers.xml_manager.get_application(appid)
		return wrap_application(x)

	def get_top_objects(self, params):
		appid = params["appid"]
		x = managers.xml_manager.get_application(appid)
		return wrap_objects_list(x.objects_list)

	def get_child_objects(self, params):
		appid = params["appid"]
		objid = params["objid"]
		x = managers.xml_manager.get_application(appid)
		obj = x.search_object(objid)
		if obj:
			return wrap_objects_list(obj.objects_list)

	def get_object(self, params):
		appid = params["appid"]
		objid = params["objid"]
		x = managers.xml_manager.get_application(appid)
		obj = x.search_object(objid)
		if obj:
			return wrap_object(obj)

	def get_child_objects_tree(self, params):
		appid = params["appid"]
		objid = params["objid"]
		x = managers.xml_manager.get_application(appid)
		obj = x.search_object(objid)
		if obj:
			return wrap_objects_tree(obj)

	def object_get_number_of_childs(self, params):
		appid = params["appid"]
		objid = params["objid"]
		x = managers.xml_manager.get_application(appid)
		obj = x.search_object(objid)
		if obj:
			return str(len(obj.get_all_children()))
		return "0"

	def get_application_structure(self, params):
		appid = params["appid"]
		x = managers.xml_manager.get_application(appid)
		return x.structure_element.toxml()

	#def set_application_structure(self, params):
	#	appid = params["appid"]
	#	data = params["data"]
	#	x = managers.xml_manager.get_application(appid)
	#	if x:
	#		o = xml_object(srcdata = data)
	#		x.set_structure(o)
	#		o.delete()

	def application_e2vdom(self, params):
		appid = params["appid"]
		x = managers.xml_manager.get_application(appid)
		return x.e2vdom_element.toxml()

	def application_actions(self, params):
		appid = params["appid"]
		x = managers.xml_manager.get_application(appid)
		return x.actions_element.toxml()

	def object_actions(self, params):
		appid = params["appid"]
		objid = params["objid"]
		x = managers.xml_manager.get_application(appid)
		obj = x.search_object(objid)
		if obj:
			return obj.actions_element.toxml()

	def application_get_info(self, params):
		appid = params["appid"]
		app = managers.xml_manager.get_application(appid)
		return wrap_application_info(app)

	#def application_set_info(self, params):
	#	appid = params["appid"]
	#	data = params["data"]
	#	request_manager.current.user = params["username"]
	#	app = managers.xml_manager.get_application(appid)
	#	if app:
	#		param = parse_attr(data)
	#		if param:
	#			for key in param:
	#				app.set_info(key, param[key])
	#			app.sync()
	#		return "OK"

	def application_number_of_objects(self, params):
		appid = params["appid"]
		app = managers.xml_manager.get_application(appid)
		return str(app.objects_amount())

	#def save_object(self, params):
	#	appid = params["appid"]
	#	objid = params["objid"]
	#	data = params["data"]
	#	request_manager.current.user = params["username"]
	#	app = managers.xml_manager.get_application(appid)
	#	if app:
	#		obj = app.search_object(objid)
	#		if obj:
	#			x = VDOM_object_wrapper(None, data = data)
	#			obj.set_name(x.original_name)
	#			for a in x.attr_names:
	#				obj.set_attribute(a, getattr(x, a), do_compute = False)

	# --- source ---------------------------------------------------------------

	#def get_source(self, params):
	#	appid = params["appid"]
	#	objid = params["objid"]
	#	action = params["action"]
	#	context = params["context"]
	#	x = managers.xml_manager.get_application(appid)
	#	if x:
	#		obj = x.search_object(objid)
	#		if obj:
	#			return source_cache.get_source(x, obj, action, context)


from memory.xml_object import xml_object
