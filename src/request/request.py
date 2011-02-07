"""request module represents the request got by the VDOM server"""

import os, sys, cgi, shutil
from cStringIO import StringIO
from cgi import FieldStorage

from environment import VDOM_environment
from headers import VDOM_headers
from arguments import VDOM_request_arguments
from Cookie import BaseCookie
from src.xml.interface import VDOM_memory_interface
import src.managers
import src.engine

class MFSt(FieldStorage):

	def make_file(self, binary=None):
		import tempfile
		return tempfile.NamedTemporaryFile("w+b",dir=VDOM_CONFIG["TEMP-DIRECTORY"])

class File_argument(object):
	def __init__(self,fileobj, name):
		self.__fileobj = fileobj
		self.__name = name
	def __getitem__(self, key):
		if not isinstance(key, int):
			raise TypeError
		if key == 0:
			self.__fileobj.seek(0)
			value = self.__fileobj.read()
			self.__fileobj.seek(0)
			return value
		elif key == 1:
			return self.__name
		else:
			raise AttributeError

class VDOM_request:
	"""VDOM server request object"""

	#------------------------------------------------------------
	def __init__(self, arguments):
		""" Constructor, create headers, cookies, request and environment """
		headers = arguments["headers"]
		handler = arguments["handler"]

		#debug("Incoming headers---")
		#for h in headers:
		#	debug(h + ": " + headers[h])
		#debug('-'*40)

		self.__headers = VDOM_headers(headers)
		self.__headers_out = VDOM_headers({})

		self.__cookies = BaseCookie(headers.get("cookie"))
		self.__environment = VDOM_environment(headers, handler)
		self.files = {}
		args = {}
		#parse request data depenging on the request method
		if arguments["method"] == "post":
			try:
				if self.environment().environment()["REQUEST_URI"] != VDOM_CONFIG["SOAP-POST-URL"]:
					storage = MFSt(handler.rfile, headers, "", self.__environment.environment(), True)
					for key in storage.keys():
						#Access to file name after uploading
						filename = getattr(storage[key],"filename","")
						if filename and storage[key].file:
							args[key] = File_argument(storage[key].file,filename)
							self.files[key] = [storage[key].file,filename]
						else:
							args[key] = storage.getlist(key)
						if filename:
							args[key+"_filename"] = [filename]
				else:
					self.postdata = handler.rfile.read(int(self.__headers.header("Content-length")))
			except: pass
		try:
			args1 = cgi.parse_qs(self.__environment.environment()["QUERY_STRING"], True)
			for key in args1.keys():
				args[key] = args1[key]
		except:
			pass

		self.fault_type_http_code = 500
		if "user-agent" in self.__headers.headers():
			if "adobeair" in self.__headers.headers()["user-agent"].lower():
				self.fault_type_http_code = 200

		# session
		sid = ""
		cookies = self.__cookies #.cookies()
		if "sid" in args:
			#debug("Got session from arguments "+str(args["sid"]))
			sid = args["sid"]
		elif "sid" in cookies:
			#debug("Got session from cookies "+cookies["sid"].value)
			sid = cookies["sid"].value
		if sid == "":
			sid = src.managers.session_manager.create_session()
			#debug("Created session " + sid)
		else:
			x = src.managers.session_manager[sid]
			if x is None:
				debug("Session " + sid + " expired")
				sid = src.managers.session_manager.create_session()
		#debug("Session ID "+str(sid))
		cookies["sid"] = sid
		args["sid"] = sid
		self.__session = src.managers.session_manager[sid]

		self.__arguments = VDOM_request_arguments(args)
		self.__server = handler.server
		self.__handler = handler
		self.app_vhname = self.__environment.environment()["HTTP_HOST"].lower()
		vh = handler.server.virtual_hosting()
		self.__app_id = vh.get_site(self.app_vhname)
		if not self.__app_id:
			self.__app_id = vh.get_def_site()
		self.__stdout = StringIO()
		self.action_result = ""

		self.application_id = self.__app_id
		self.sid = sid
		self.method = arguments["method"]
		self.vdom = VDOM_memory_interface(self)

		self.args = self.__arguments
		try:
			self.__app = src.managers.xml_manager.get_application(self.__app_id)
		except:
			self.__app = None
		# special flags
		self.redirect_to = None
		self.wfile = handler.wfile
		self.__nocache = False
		self.nokeepalive = False
		self.__binary = False
		self.fh = None
	
	def __del__(self):
		"""Destructor needed for temp files cleanup"""
		for key in self.files:
			self.files[key][0].close()
			
	def add_client_action(self, obj_id, data):
		self.action_result += data

	def binary(self, b = None):
		if b is not None:
			self.__binary = b
		return self.__binary

	def set_nocache(self):
		if not self.__nocache:
			self.__handler.send_response(200)
			self.__handler.send_headers()
			self.__handler.end_headers() #TODO!
			self.wfile.write(self.output())
			#self.wfile.write('\n')
		self.__nocache = True
		self.nokeepalive = True

	def set_application_id(self, application_id):
		self.__app_id=application_id
		self.application_id=application_id
		try: self.__app = src.managers.xml_manager.get_application(self.__app_id)
		except: pass

	def write(self, string = None):
		"""save output"""
		if string:
			if self.__nocache:
				self.wfile.write(string)
				#self.wfile.write('\n')
			else:
				self.__stdout.write(string)
				self.__stdout.write('\n')

	def write_handler(self, handler):
		"""writing into stream from file handler"""
		self.fh = handler

	def content_length(self):
		"""get output length"""
		return self.__stdout.len

	def output(self):
		"""get output"""
		value = self.__stdout.getvalue()
		del self.__stdout
		self.__stdout = StringIO()
		return value

	def server(self, server = None):
		""" server object """
		return self.__server

	def session(self):
		"""session object"""
		return self.__session

	def set_session_id(self, sid):
		self.__cookies["sid"] = sid
		self.args.arguments()["sid"] = sid
		self.__session = src.managers.session_manager[sid]

	def headers(self, headers = None):
		""" Server headers. """
		return self.__headers

	def headers_out(self, headers = None):
		""" Server headers. """
		return self.__headers_out

	def environment(self, environment = None):
		""" Server environment """
		return self.__environment

	def arguments(self, args = None):
		""" request arguments """
		return self.__arguments

	def cookies(self):
		""" Server cookies """
		return self.__cookies

	def application(self):
		"""get application object"""
		return self.__app

	def handler(self):
		return self.__handler

	def app_id(self):
		"""get application identifier"""
		return self.__app_id

	def redirect(self, to):
		"""specify redirection to some url"""
		self.redirect_to = to

	def add_header(self, name, value):
		"""add header"""
		headers = self.__headers_out.headers()
		headers[name] = value

	def send_file(self, filename, length, handler, content_type=None):
		f_content_type = content_type if content_type else "application/octet-stream"
		self.add_header("Content-type", f_content_type)
		if content_type:
			self.add_header("Content-Disposition", "inline; filename=\"%s\""%filename)
		else:
			self.add_header("Content-Disposition", "attachment; filename=\"%s\""%filename)
		self.add_header("Content-Length",str(length))
		self.set_nocache()
		self.write_handler(handler)
