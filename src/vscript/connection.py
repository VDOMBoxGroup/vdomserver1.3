
import errors, types, urllib, urllib2, httplib, mimetools, codecs
from StringIO import StringIO

from array import array
from empty import empty, v_empty
from null import null, v_null
from integer import integer
from double import double, nan, infinity
from date import date
from string import string
from boolean import boolean, v_true_value, v_false_value
from generic import generic
from nothing import nothing, v_nothing
from variant import variant
from constant import constant
from shadow import shadow
from binary import binary

from . import byref, byval
from auxiliary import as_value, as_is, as_array, as_integer, as_double, as_string, as_boolean, as_generic, as_date, as_binary
from auxiliary import pack, unpack, adapt



v_connectionerror=urllib2.URLError



class v_proxy(generic):

	def __init__(self):
		generic.__init__(self)
		self.value={}

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			self.let(*arguments, **keywords)
		elif "set" in keywords:
			self.set(*arguments, **keywords)
		else:
			# Experimental hack to simulate non-object behaviour
			# Allow both let and set assigment and pass as_value for example
			if arguments:
				return self.get(*arguments, **keywords)
			else:
				return self



	def get(self, key, *arguments, **keywords):
		if arguments:
			raise errors.wrong_number_of_arguments
		return self.values[as_string(key)]

	def let(self, *arguments, **keywords):
		if not arguments:
			return keywords["set"]
		if len(arguments)>1:
			raise errors.wrong_number_of_arguments
		self.values[as_string(arguments[0])]=as_string(keywords["let"])

	def set(self, *arguments, **keywords):
		raise errors.type_mismatch		



	def build_handler(self):
		return urllib2.ProxyHandler(self.value)



class v_httppasswordmanager(generic):


	def __init__(self):
		generic.__init__(self)
		self.username=None
		self.password=None



	def v_username(self, let=None, set=None):
		if let is not None:
			self.username=as_string(let)
		elif set is not None:
			raise errors.object_has_no_property("username")
		else:
			return string(self.username) if self.username else v_null

	def v_password(self, let=None, set=None):
		if let is not None:
			self.password=as_string(let)
		elif set is not None:
			raise errors.object_has_no_property("password")
		else:
			return string(self.password) if self.password else v_null


	
	def build_handler(self, proxy):
		http_proxy=proxy.value.get("http", None)
		if http_proxy:
			if not http_proxy.starts_with("http://"):
				http_proxy="http://"+http_proxy
			password_manager=urllib2.HTTPPasswordMgrWithDefaultRealm()
			password_manager.add_password(None, http_proxy, self.username, self.password)
			return urllib2.ProxyBasicAuthHandler(password_manager)
		else:
			return None



class v_connection(generic):

	def __init__(self):
		generic.__init__(self)
		self.value=None
		self.encoding=None
		self.codec=None
		self.proxy=None
		self.authentication=None
		self.timeout=None
		

	
	def erase(self):
		if self.value:
			try:
				self.value.close()
			except httplib.HTTPException as error:
				raise urllib2.URLError(error)
			self.value=None

	def assume(self, encoding):
		try:
			codec=codecs.lookup(encoding)
			self.encoding=encoding
			self.codec=codec
		except LookupError:
			pass


			
	def v_open(self, url):
		if self.value:
			raise errors.invalid_procedure_call(name=u"open")
		try:
			handlers, parameters=[], {}
			if self.proxy:
				handlers.append(self.proxy.build_handler())
				if self.authentication:
					handler=self.authentication.build_handler(self.proxy)
					if handler:
						handlers.append(handler)
			opener=urllib2.build_opener(*handlers)
			if self.timeout:
				parameters["timeout"]=self.timeout
			self.value=opener.open(as_string(url), **parameters)
		except httplib.HTTPException as error:
			raise urllib2.URLError(error)
		if self.value.url.startswith("http://"):
			mime=mimetools.Message(StringIO(self.value.info()))
			self.assume(mime.getparam("charset"))

	def v_read(self):
		if not self.value:
			raise errors.invalid_procedure_call(name=u"read")
		try:
			data=self.value.read()
		except httplib.HTTPException as error:
			raise urllib2.URLError(error)
		if self.codec:
			try:
				return string(self.codec.decode(data))
			except UnicodeError:
				raise errors.invalid_procedure_call(name=u"read")
		else:
			return binary(data)

	def v_write(self, data):
		if not self.value:
			raise errors.invalid_procedure_call(name=u"write")
		data=as_value(data)
		if self.codec:
			try:
				data=self.codec.encode(as_string(data))
			except UnicodeError:
				raise errors.invalid_procedure_call(name=u"write")
		else:
			data=as_binary(data)
		try:
			self.value.write(data)
		except httplib.HTTPException as error:
			raise urllib2.URLError(error)

	def v_close(self):
		if not self.value:
			raise errors.invalid_procedure_call(name=u"close")
		self.erase()



	def v_encoding(self, let=None, set=None):
		if let is not None:
			self.assume(as_string(let))
		elif set is not None:
			raise errors.object_has_no_property("encoding")
		else:
			return string(self.encoding) if self.encoding else v_null

	def v_proxy(self, let=None, set=None):
		if let is not None:
			raise errors.object_has_no_property("proxy")
		elif set is not None:
			self.proxy=as_generic(set, specific=v_proxy)
		else:
			return self.proxy or v_nothing
