"""server request handler module"""

import sys, os, posixpath, urllib, shutil, mimetypes, thread, re, socket, threading, time, SOAPpy, traceback, select, cgi

if sys.platform.startswith("freebsd"):
	import vdomlib

import SocketServer, BaseHTTPServer, SimpleHTTPServer, socket
from cStringIO import StringIO
import xml.sax.saxutils
import webdav_server
from wsgidav.wsgidav_app import WsgiDAVApp
from wsgiref.util import guess_scheme

import managers
from request.request import VDOM_request
from storage.storage import VDOM_config
from version import *
import soap.SOAPBuilder
from soap.wsdl import methods as soap_methods
from utils.exception import VDOM_exception, VDOM_exception_missing_app


# A class to describe how header messages are handled
class HeaderHandler:
	# Initially fail out if there are any problems.
	def __init__(self, header, attrs):
		for i in header.__dict__.keys():
			if i[0] == "_":
				continue

			d = getattr(header, i)

			try:
				fault = int(attrs[id(d)][(NS.ENV, 'mustUnderstand')])
			except:
				fault = 0

			if fault:
				raise faultType, ("%s:MustUnderstand" % NS.ENV_T,
						  "Required Header Misunderstood",
						  "%s" % i)

# for the soap handler
_contexts = dict()

class VDOM_http_request_handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	"""VDOM http request handler"""

	"""server version string"""
	server_version = VDOM_server_name

	def __init__(self, request, client_address, server, args=None):
		"""constructor"""
		#debug("Creating RequestHandler object")
		self.__reject = args["reject"]
		self.__deny = args["deny"]
		self.__card = args["card"]
		self.__limit = args["limit"]
		self.__connections = args["connections"]
		"""call base class constructor"""
		try:
			SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
		except:
			raise
	
	def start_response(self, status, response_headers, exc_info=None):
		if exc_info:
			try:
				raise exc_info[0], exc_info[1], exc_info[2]
				# do stuff w/exc_info here
			finally:
				exc_info = None    # Avoid circular ref.
		status_code = int(status.split(' ')[0])
		status_message = status[status.find(' ')+1:]
		try:
			self.send_response(status_code, status_message)
		except socket.error as e:#TODO: find why socket already closed when error in Webdav
			return
		for header in response_headers:
			if header[0] != 'Date':
				self.send_header(header[0], header[1])
				
		cookies = self.__request.cookies()
		if "sid" in cookies:
			cookies["sid"]["path"] = "/"
			self.wfile.write("%s\r\n" % cookies.output())
			
		self.end_headers()
		#print response_headers
		#_str = '\n'.join( traceback.format_stack() )
		#print _str
		#cgi.escape( str )		
		return self.wfile.write

	def get_environ(self):
		env = self.__request.environment().environment().copy()
		#env = {}
		env['wsgi.input']        = self.rfile
		env['wsgi.errors']       = sys.stderr
		env['wsgi.version']      = (1, 0)
		env['wsgi.run_once']     = False
		env['wsgi.url_scheme']   = guess_scheme(env)
		env['wsgi.multithread']  = True
		env['wsgi.multiprocess'] = True
		env['SERVER_PROTOCOL'] = self.request_version
		env['REQUEST_METHOD'] = self.command
		if '?' in self.path:
			path,query = self.path.split('?',1)
		else:
			path,query = self.path,''
		
		env['PATH_INFO'] = urllib.unquote(path)
		env['QUERY_STRING'] = query
		
		host = self.address_string()
		if host != self.client_address[0]:
			env['REMOTE_HOST'] = host
		env['REMOTE_ADDR'] = self.client_address[0]
		
		if self.headers.typeheader is None:
			env['CONTENT_TYPE'] = self.headers.type
		else:
			env['CONTENT_TYPE'] = self.headers.typeheader
		
		length = self.headers.getheader('content-length')
		if length:
			env['CONTENT_LENGTH'] = length
		script_name = env.get('SCRIPT_NAME')
		if script_name:
			env['SCRIPT_NAME'] = script_name.rstrip("/")
		
		for h in self.headers.headers:
			k,v = h.split(':',1)
			k=k.replace('-','_').upper(); v=v.strip()
			if k in env:
				continue                    # skip content length, type,etc.
			if 'HTTP_'+k in env:
				if 'HTTP_'+k not in self.__request.environment().environment():
					env['HTTP_'+k] += ','+v     # comma-separate multiple headers
			else:
				env['HTTP_'+k] = v
		return env

	def handle_one_request(self):
		"""Handle a single HTTP request.
	
		You normally don't need to override this method; see the class
		__doc__ string for information on how to handle specific HTTP
		commands such as GET and POST.
	
		"""
		try:
			self.raw_requestline = self.rfile.readline()
			if not self.raw_requestline:
				self.close_connection = 1
				return
			if not self.parse_request():
				# An error code has been sent, just exit
				return
			mname = 'do_' + self.command
			host = self.headers.get("host")
   
			vh = managers.virtual_hosts
			
			app_id = (vh.get_site(host.lower()) if host else None) or vh.get_def_site()
			if not app_id:
				managers.xml_manager.load_apps()	
			self.wsgidav_app = None
			if app_id:
				try:
					managers.xml_manager.load_application_by_guid(app_id)					
					appl = managers.xml_manager.get_application(app_id)
					self.wsgidav_app = getattr(appl, 'wsgidav_app', None)
				except VDOM_exception_missing_app as e:
					debug(e)			
				else:
					#dav_map = getattr(appl,"dav_map",None)
					#if not dav_map:
					#	appl.dav_map = set()
					#	dav_map = appl.dav_map
					#	for obj in appl.get_objects_list():
					#		if obj.type.id == '1a43b186-5c83-92fa-7a7f-5b6c252df941':
					#			dav_map.add("/" + obj.name)
					#for realm in dav_map:    
					#	if self.path.startswith(realm):
					#		mname = 'do_WebDAV'
					realm = self.path.strip("/").split("/").pop(0)
					objects_list = appl.search_objects_by_name(realm)
					for o in objects_list:
						if managers.webdav_manager.get_webdav_share_path(appl.id, o.id) != None:
							self.wsgidav_app = appl.wsgidav_app
							mname = 'do_WebDAV'
							break
						
			if self.command not in ("GET", "POST"):
				mname = 'do_WebDAV'
			
			if not hasattr(self, mname):
				self.send_error(501, "Unsupported method (%r)" % self.command)
				return
			method = getattr(self, mname)
			method()
			self.wfile.flush() #actually send the response if not already done.
		except socket.timeout, e:
			#a read or a write timed out.  Discard this connection
			self.log_error("Request timed out: %r", e)
			self.close_connection = 1
			return	
	
	def handle(self):
		"""Handle multiple requests if necessary."""
		self.close_connection = 1
		self.handle_one_request()
		while self.server.active and not self.close_connection:
			ready=select.select([self.request], [], [], 0.5)
			if not ready[0]: continue
			self.handle_one_request()

	def do_WebDAV(self):
		if self.__reject:
			self.send_error(503, self.responses[503][0])
			return None		
		self.create_request(self.command.lower())
		environ = self.get_environ()
		application = self.wsgidav_app
		if not application:
			self.send_error(404, self.responses[404][0])
		elif environ["REQUEST_METHOD"] == "OPTIONS" and environ["PATH_INFO"] in ("/", "*"):
			import wsgidav.util as util
			self.start_response("200 OK", [("Content-Type", "text/html"),
					                    ("Content-Length", "0"),
					                    ("DAV", "1,2"),
					                    ("Server", "DAV/2"),
					                    ("Date", util.getRfc1123Time()),
					                    ])		
			
		else:
			for v in application(environ, self.start_response):
				self.wfile.write(v)
		
		
	def do_GET(self):
		"""serve a GET request"""
		# create request object
		#debug("DO GET %s"%self)
		self.create_request("get")
		f = self.on_request("get")
		if f:
			sys.setcheckinterval(0)
			shutil.copyfileobj(f, self.wfile)
			sys.setcheckinterval(100)
			#self.copyfile(f, self.wfile)
			f.close()
		if not self.wfile.closed:
			if self.__request.nokeepalive:
				self.close_connection = 1
		
	def do_HEAD(self):
		"""serve a HEAD request"""
		# create request object
		self.create_request("get")
		f = self.on_request("get")
		if f:
			f.close()

	def do_POST(self):
		"""serve a POST request"""
		# create request object
		#debug("DO POST %s"%self)
		self.create_request("post")
		# if POST to SOAP-POST-URL call do_SOAP
		if self.__request.environment().environment()["REQUEST_URI"] == VDOM_CONFIG["SOAP-POST-URL"]:
			if self.__card:
				self.do_SOAP()
			return
		f = self.on_request("post")
		if f:
			sys.setcheckinterval(0)
			shutil.copyfileobj(f, self.wfile)
			sys.setcheckinterval(100)
			#self.copyfile(f, self.wfile)
			f.close()
		#if not self.wfile.closed:
		#	if self.__request.nokeepalive:
		#		self.close_connection = 1		

	def create_request(self, method):
		"""initialize request, <method> is either 'post' or 'get'"""
		#debug("CREATE REQUEST %s"%self)
		#import gc
		#debug("\nGarbage: "+str(len(gc.garbage))+"\n")
		#debug("Creating request object")
		args = {}
		args["headers"] = self.headers
		args["handler"] = self
		args["method"] = method
		self.__request = VDOM_request(args)
		self.__request.number_of_connections = self.__connections
		#debug("Creating request object complete")
		# put request to the manager
		managers.request_manager.current = self.__request

		if "127.0.0.1" != self.client_address[0]:
			debug("Session is " + self.__request.sid)

	def on_request(self, method):
		"""request handling code the method <method>"""
		#debug("ON REQUEST %s"%self)
		#check if we should send 503 or 403 errors
		if self.__reject:
			self.send_error(503, self.responses[503][0])
			return None
		if self.__deny:
			self.send_error(403, self.responses[403][0])
			return None
		if not self.__card:
			data = _("Please insert your card")
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.send_header("Content-Length", str(len(data)))
			self.end_headers()
			return StringIO(data)
		if not self.__limit:
			data = _("License exceeded")
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.send_header("Content-Length", str(len(data)))
			self.end_headers()
			return StringIO(data)
		# check if requested for wsdl file - then return it
		if self.__request.environment().environment()["REQUEST_URI"] == VDOM_CONFIG["WSDL-FILE-URL"]:
			wsdl = self.server.get_wsdl()
			self.send_response(200)
			self.send_header("Content-type", "text/xml")
			self.send_header("Content-Length", str(len(wsdl)))
			self.end_headers()
			return StringIO(wsdl)
		if self.__request.environment().environment()["REQUEST_URI"] == "/crossdomain.xml":
			data = """<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM
"http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
 <site-control permitted-cross-domain-policies="all"/>
 <allow-access-from domain="*" secure="false"/>
 <allow-http-request-headers-from domain="*" headers="*" secure="false"/>
</cross-domain-policy>"""
			self.send_response(200)
			self.send_header("Content-type", "text/xml")
			self.send_header("Content-Length", str(len(data)))
			self.end_headers()
			return StringIO(data)
		# management
		if self.__request.environment().environment()["REQUEST_URI"] == VDOM_CONFIG["MANAGEMENT-URL"]:
			return self.redirect("/index.py")
		# process requested URI, call module manager
		try:
			(code, ret) = managers.module_manager.process_request(self.__request)
			self.__request.collect_files()
		except Exception as e:
			requestline = "<br>"
			if hasattr(self, "requestline"):
				requestline = "<br>" + self.requestline + "<br>" + '-'*80
			if not hasattr(self, "request_version"):
				self.request_version = "HTTP/1.1"
			fe = "".join(["<br><br>", '-'*80, requestline, "<br>Exception happened during processing of request:", 
				      traceback.format_exc(), '-'*40])
			self.__request.collect_files()
			self.send_error(500, excinfo=fe)
			return None
		
			
		# check redirect
		if self.__request.redirect_to:
			return self.redirect(self.__request.redirect_to)
		elif ret:
			self.send_response(200)
			ret_len = None
			if isinstance(ret, file):
				ret.seek(0,2)
				ret_len = str(ret.tell())
				ret.seek(0)
			else:
				ret_len = str(len(ret))
			self.__request.add_header("Content-Length", ret_len)
			if self.__request.nokeepalive:
				self.__request.add_header("Connection", "Close")
			else:
				self.__request.add_header("Connection", "Keep-Alive")
			# cookies
			#if len(self.__request.cookies())>0:
			#	for key in self.__request.cookies():
			#		self.__request.add_header("Set-cookie",self.__request.cookies()[key].output())
				#self.__request.add_header("Set-cookie",self.__request.cookies().output())
			#if len(self.__request.cookies().cookies()) > 0:
				#self.__request.add_header("Set-cookie", self.__request.cookies().get_string())
			self.send_headers()
			self.end_headers()
			if isinstance(ret, file):
				if sys.platform.startswith("freebsd"):
					vdomlib.sendres(self.wfile.fileno(), ret.fileno(), int(ret_len))
					ret.close()
					return None
				else:
					return ret
			else:
				return StringIO(ret)
		elif "" == ret:
			return None
		elif code:
			self.send_error(code, self.responses[code][0])
			return None
		else:
			self.send_error(404, self.responses[404][0])
			return None

	def send_headers(self):
		"""send all headers"""
		headers = self.__request.headers_out().headers()
		cookies = self.__request.cookies().output()
		#debug("Outgoing headers---")
		#for h in headers:
		#	debug(h + ": " + headers[h])
		#debug('-'*40)
		for hh in headers:
			#debug(hh + " : " + headers[hh])
			self.send_header(hh, headers[hh])
		if len(cookies)>0:
			self.wfile.write("%s\r\n" % cookies)

	def finish(self):
		"""finish processing request"""
		#debug("FINISH REQUEST %s"%self)
		SimpleHTTPServer.SimpleHTTPRequestHandler.finish(self)
		"""tell the server that processing is finished"""
		self.server.notify_finish(self.client_address)
		# remove request
		del managers.request_manager.current
		try:
			del(self.__request.vdom)
			del(self.__request)
		except: pass

	def redirect(self, to):
		self.send_response(302)
		#if len(self.__request.cookies)>0:
		#	for key in self.__request.cookies():
		#			self.__request.add_header("Set-cookie",self.__request.cookies()[key].output())
			#self.__request.add_header(self.__request.cookies.output())		
		#if len(self.__request.cookies().cookies()) > 0:
		#	self.__request.add_header("Set-cookie", self.__request.cookies().get_string())
		self.__request.add_header("Location", to)
		self.send_headers()
		self.end_headers()
		return StringIO()

	def log_message(self, format, *args):
		"""log an arbitrary message to stderr"""
		if "127.0.0.1" != self.client_address[0]:
			debug("%s %s {%d}" % (self.address_string(), format%args, self.server.get_cur_con()))
		#sys.stderr.write("%s - Thread %d - [%s] %s {%d}\n" % (self.address_string(), thread.get_ident(), self.log_date_time_string(), format%args, self.server.get_cur_con()))

	def print_list(self, list, f):
		"""print contents of the dictionary in the form of list"""
		for k in list.keys():
			f.write("%s: \"%s\"<br>\n" % (k.upper(), list[k]))
		f.write("<hr>")

	def address_string(self):
		"""Return the client address formatted for logging"""
		host, port = self.client_address[:2]
		return host

	def sample_page(self, method):
		"""generate sample output page"""
		debug("Returning sample page")
		f = StringIO()
		f.write("<b>Application id:</b> %s<br>" % str(self.__request.app_id()))
		f.write("<b>Registered types:</b><br>")
		mngr = managers.xml_manager
		typelst = mngr.get_types()
		for typeid in typelst:
			tp = None
			try: tp = mngr.get_type(typeid)
			except: pass
			if tp:
				typename = tp.name
				if "" == typename:
					typename = _("Not specified")
				f.write("%s %s<br>" % (typename, typeid))
		f.write("<b>Registered applications:</b><br>")
		applst = mngr.get_applications()
		for appid in applst:
			app = None
			try: app = mngr.get_application(appid)
			except: pass
			if app:
				appname = app.name
				if "" == appname:
					appname = _("Not specified")
				f.write("%s %s&nbsp;" % (appname, appid))
				f.write("[")
				for o in app.get_objects_list():
					f.write("%s&nbsp;" % o.id)
				f.write("]<br>")
		f.write("<hr>\n")
		f.write("<h2>Sample output for the %s method:</h2><hr>\n" % method.upper())
		f.write("<h2>Request headers:</h2>\n")
		self.print_list(self.__request.headers().headers(), f)
		f.write("<h2>Cookies:</h2>\n")
		self.print_list(self.__request.cookies().cookies(), f)
		f.write("<h2>Environment:</h2>\n")
		self.print_list(self.__request.environment().environment(), f)
		f.write("<h2>Request arguments:</h2>\n")
		f.write(str(self.__request.arguments().arguments()))
		f.write("<hr>\n")
		length = f.tell()
		f.seek(0)
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-Length", str(length))
		self.end_headers()
		return f

	def do_SOAP(self):
		global _contexts
		status = 500

		VDOM_debug = 0
		dumpSOAPIn = 0
		dumpSOAPOut = 0
		dumpHeadersIn = 0
		dumpHeadersOut = 0

		cf = VDOM_config()
		#No more alot of debug while soap
		#if "1" == cf.get_opt("DEBUG"):       
		#	VDOM_debug = 1
		#	dumpSOAPIn = 1
		#	dumpSOAPOut = 1
		#	dumpHeadersIn = 1
		#	dumpHeadersOut = 1

		try:
			if dumpHeadersIn:
				s = 'Incoming HTTP headers'
				SOAPpy.debugHeader(s)
				debug(self.raw_requestline.strip())
				debug("\n".join(map (lambda x: x.strip(), self.headers.headers)))
				SOAPpy.debugFooter(s)
			data = self.__request.postdata
			if dumpSOAPIn:
				s = 'Incoming SOAP'
				SOAPpy.debugHeader(s)
				debug(data)
				SOAPpy.debugFooter(s)

			(r, header, body, attrs) = SOAPpy.parseSOAPRPC(data, header = 1, body = 1, attrs = 1)

			method = r._name
			args = r._aslist()
			kw = r._asdict()

			# TODO:
			# check if there are list items in args or kw
			# and leave only the first element

			if SOAPpy.Config.simplify_objects:
				args = simplify(args)
				kw = simplify(kw)

			# Handle mixed named and unnamed arguments by assuming
			# that all arguments with names of the form "v[0-9]+"
			# are unnamed and should be passed in numeric order,
			# other arguments are named and should be passed using
			# this name.

			# This is a non-standard exension to the SOAP protocol,
			# but is supported by Apache AXIS.

			# It is enabled by default.  To disable, set
			# Config.specialArgs to False.

			if SOAPpy.Config.specialArgs: 

				ordered_args = {}
				named_args   = {}

				for (k,v) in  kw.items():

					if k[0]=="v":
						try:
							i = int(k[1:])
							ordered_args[i] = v
						except ValueError:
							named_args[str(k)] = v

					else:
						named_args[str(k)] = v

			# We have to decide namespace precedence
			# I'm happy with the following scenario
			# if r._ns is specified use it, if not check for
			# a path, if it's specified convert it and use it as the
			# namespace. If both are specified, use r._ns.

			ns = r._ns

			if len(self.path) > 1 and not ns:
				ns = self.path.replace("/", ":")
				if ns[0] == ":": ns = ns[1:]

			# authorization method
			a = None

			keylist = ordered_args.keys()
			keylist.sort()

			# create list in proper order w/o names
			tmp = map( lambda x: ordered_args[x], keylist)
			ordered_args = tmp

#			print '<-> Argument Matching Yielded:'
#			print '<-> Ordered Arguments:' + str(ordered_args)
#			print '<-> Named Arguments  :' + str(named_args)

			arg_names = soap_methods[method]
			if "sid" in arg_names:
				_i = arg_names.index("sid")
				if _i < len(ordered_args):
					managers.request_manager.current.set_session_id(ordered_args[_i])
				elif "sid" in named_args:
					managers.request_manager.current.set_session_id(named_args["sid"])
			if "appid" in arg_names:
				_i = arg_names.index("appid")
				if _i < len(ordered_args):
					managers.request_manager.current.set_application_id(ordered_args[_i])
				elif "appid" in named_args:
					managers.request_manager.current.set_application_id(named_args["appid"])

			resp = ""

			# For fault messages
			if ns:
				nsmethod = "%s:%s" % (ns, method)
			else:
				nsmethod = method

			try:
				# First look for registered functions
				if ns in self.server.funcmap and method in self.server.funcmap[ns]:
					f = self.server.funcmap[ns][method]

					# look for the authorization method
					if self.server.config.authMethod != None:
						authmethod = self.server.config.authMethod
						if ns in self.server.funcmap and authmethod in self.server.funcmap[ns]:
							a = self.server.funcmap[ns][authmethod]
				else:
					# Now look at registered objects
					# Check for nested attributes. This works even if
					# there are none, because the split will return
					# [method]
					f = self.server.objmap[ns]

					# Look for the authorization method
					if self.server.config.authMethod != None:
						authmethod = self.server.config.authMethod
						if hasattr(f, authmethod):
							a = getattr(f, authmethod)

					# then continue looking for the method
					l = method.split(".")
					for i in l:
						f = getattr(f, i)
			except:
				info = sys.exc_info()
				try:
					resp = SOAPpy.buildSOAP(SOAPpy.faultType("%s:Client" % SOAPpy.NS.ENV_T, "Method Not Found",
										 "%s : %s %s %s" % (nsmethod,
												    info[0],
												    info[1],
												    info[2])),
								encoding = self.server.encoding,
								config = self.server.config)
				finally:
					del info
				status = self.__request.fault_type_http_code
			else:
				try:
					if header:
						x = HeaderHandler(header, attrs)

					fr = 1

					# call context book keeping
					# We're stuffing the method into the soapaction if there
					# isn't one, someday, we'll set that on the client
					# and it won't be necessary here
					# for now we're doing both

					if "SOAPAction".lower() not in self.headers.keys() or self.headers["SOAPAction"] == "\"\"":
						self.headers["SOAPAction"] = method

					thread_id = thread.get_ident()
					_contexts[thread_id] = SOAPpy.SOAPContext(header, body,
										  attrs, data,
										  self.connection,
										  self.headers,
										  self.headers["SOAPAction"])

					# Do an authorization check
					if a != None:
						if not a(None, **{"_SOAPContext" :
								     _contexts[thread_id] }):
							raise SOAPpy.faultType("%s:Server" % SOAPpy.NS.ENV_T,
									       "Authorization failed.",
									       "%s" % nsmethod)

					# If it's wrapped, some special action may be needed
					if isinstance(f, SOAPpy.MethodSig):
						c = None

						if f.context:  # retrieve context object
							c = _contexts[thread_id]

## log
						if c:
							info = c.connection.getpeername()
							debug("Web service request from %s:%s - %s" % (info[0], info[1], c.soapaction))
#######

						if SOAPpy.Config.specialArgs:
							if c:
								named_args["_SOAPContext"] = c
							fr = f(*ordered_args, **named_args)
						elif f.keywords:
							# This is lame, but have to de-unicode
							# keywords

							strkw = {}

							for (k, v) in kw.items():
								strkw[str(k)] = v
							if c:
								strkw["_SOAPContext"] = c
							fr = f(None, **strkw)
						elif c:
							fr = f(*args, **{'_SOAPContext':c})
						else:
							fr = f(*args, **{})

					else:
						if SOAPpy.Config.specialArgs:
							fr = f(*ordered_args, **named_args)
						else:
							fr = f(*args, **{})


					if type(fr) == type(self) and \
					   isinstance(fr, voidType):
						resp = SOAPpy.buildSOAP(kw = {'%sResponse xmlns="http://services.vdom.net/VDOMServices"' % method: fr},
									encoding = self.server.encoding,
									config = self.server.config)
					else:
						resp = SOAPpy.buildSOAP(kw =
									{'Result': fr},
									encoding = self.server.encoding,
									config = self.server.config,
									method = method + "Response",
									namespace = ('', "http://services.vdom.net/VDOMServices"))

					# Clean up _contexts
					if thread_id in _contexts:
						del _contexts[thread_id]

				except Exception, e:
					import traceback
					info = sys.exc_info()

					try:
						if self.server.config.dumpFaultInfo and not isinstance(e, SOAPpy.faultType):
							s = 'Method %s exception' % nsmethod
							SOAPpy.debugHeader(s)
							traceback.print_exception(info[0], info[1],
										  info[2])
							SOAPpy.debugFooter(s)

						if isinstance(e, SOAPpy.faultType):
							f = e
						else:
							f = SOAPpy.faultType("%s:Server" % SOAPpy.NS.ENV_T,
									     "Method Failed",
									     "%s" % nsmethod)

						if self.server.config.returnFaultInfo:
							f._setDetail("".join(traceback.format_exception(
								info[0], info[1], info[2])))
						elif not hasattr(f, 'detail'):
							f._setDetail("%s %s" % (info[0], info[1]))
					finally:
						del info


					#method failed - return soap fault (no method tag needed)
					resp = SOAPpy.buildSOAP(f, encoding = self.server.encoding,
								config = self.server.config, namespace = "http://services.vdom.net/VDOMServices")
					status = self.__request.fault_type_http_code
				else:
					status = 200
		except SOAPpy.faultType, e:
			import traceback
			info = sys.exc_info()
			try:
				if self.server.config.dumpFaultInfo:
					s = 'Received fault exception'
					SOAPpy.debugHeader(s)
					traceback.print_exception(info[0], info[1],
								  info[2])
					SOAPpy.debugFooter(s)

				if self.server.config.returnFaultInfo:
					e._setDetail("".join(traceback.format_exception(
						info[0], info[1], info[2])))
				elif not hasattr(e, 'detail'):
					e._setDetail("%s %s" % (info[0], info[1]))
			finally:
				del info

			#method failed - return soap fault (no method tag needed)
			resp = SOAPpy.buildSOAP(e, encoding = self.server.encoding,
						config = self.server.config, namespace = "http://services.vdom.net/VDOMServices" )
			status = self.__request.fault_type_http_code
		except Exception, e:
			# internal error, report as HTTP server error

			if self.server.config.dumpFaultInfo:
				s = 'Internal exception %s' % e
				import traceback
				SOAPpy.debugHeader(s)
				info = sys.exc_info()
				try:
					traceback.print_exception(info[0], info[1], info[2])
				finally:
					del info

				SOAPpy.debugFooter(s)

			self.send_response(self.__request.fault_type_http_code)
			self.end_headers()

			if dumpHeadersOut and \
			   self.request_version != 'HTTP/0.9':
				s = 'Outgoing HTTP headers'
				SOAPpy.debugHeader(s)
				if status in self.responses:
					s = ' ' + self.responses[status][0]
				else:
					s = ''
				debug("%s %d%s" % (self.protocol_version, self.__request.fault_type_http_code, s))
				debug("Server: %s" % self.version_string())
				debug("Date: %s" % self.__last_date_time_string)
				SOAPpy.debugFooter(s)
		else:
			# got a valid SOAP response
			self.send_response(status)
			t = 'text/xml';
			if self.server.encoding != None:
				t += '; charset="%s"' % self.server.encoding
			self.send_header("Content-type", t)
			self.send_header("Content-length", str(len(resp)))
			self.end_headers()

			if dumpHeadersOut and \
			   self.request_version != 'HTTP/0.9':
				s = 'Outgoing HTTP headers'
				SOAPpy.debugHeader(s)
				if status in self.responses:
					s = ' ' + self.responses[status][0]
				else:
					s = ''
				debug("%s %d%s" % (self.protocol_version, status, s))
				debug("Server: %s" % self.version_string())
				debug("Date: %s" % self.__last_date_time_string)
				debug("Content-type: %s" % t)
				debug("Content-length: %d" % len(resp))
				SOAPpy.debugFooter(s)

			if dumpSOAPOut:
				try:
					s = 'Outgoing SOAP'
					SOAPpy.debugHeader(s)
					debug(resp)

					SOAPpy.debugFooter(s)
				except: pass

			#resp = xml.sax.saxutils.unescape(resp)
			self.wfile.write(resp)
			self.wfile.flush()

			# We should be able to shut down both a regular and an SSL
			# connection, but under Python 2.1, calling shutdown on an
			# SSL connections drops the output, so this work-around.
			# This should be investigated more someday.

			if self.server.config.SSLserver and \
			   isinstance(self.connection, SSL.Connection):
				self.connection.set_shutdown(SSL.SSL_SENT_SHUTDOWN |
							     SSL.SSL_RECEIVED_SHUTDOWN)
			else:
				#self.connection.shutdown(1)
				pass


	def date_time_string(self):
		self.__last_date_time_string = BaseHTTPServer.BaseHTTPRequestHandler.date_time_string(self)
		return self.__last_date_time_string

	def send_error(self, code, message=None, excinfo=None):
		""" send error """
		try:
			short, long=self.responses[code]
		except KeyError:
			short, long='???', '???'
		if message is None:
			message=short

		try:
			accept_language=self.headers.get("Accept-Language", "")
			separator=accept_language.find("-")
			if separator<0:
				language=VDOM_CONFIG["DEFAULT-LANGUAGE"]
			language=accept_language[0:]
		except:
			language=VDOM_CONFIG["DEFAULT-LANGUAGE"]

		filename=VDOM_CONFIG["HTTP-ERROR-PAGES-DIRECTORY"]+"/"+str(code)+".htm"

		if os.path.exists(filename):
			file=open(filename, "rb")
			content=file.read()
			file.close()

			self.send_response(code, message)
			self.send_header("Content-Type", "text/html")
			self.send_header('Connection', 'close')
			self.end_headers()
			if self.command!='HEAD' and code>=200 and code not in (204, 304):
				self.wfile.write(content)
			else:
				pass
		else:
			self.requestline = ""
			SimpleHTTPServer.SimpleHTTPRequestHandler.send_error(self, code, message)
			if excinfo:
				page_debug = VDOM_CONFIG_1["ENABLE-PAGE-DEBUG"]
				if "1" == page_debug:
					e = "<br>".join(excinfo.splitlines(True))
					self.wfile.write(e)
					self.wfile.flush()
					self.finish()

	def log_error(self, *args):
		pass

	def version_string(self):
		"""Return the server software version string."""
		return "VDOM v2 server " + VDOM_server_version + ' ' + self.sys_version
