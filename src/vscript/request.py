
import src.request

import errors, types

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



class cookies_collection_iterator(object):

	def __init__(self, iterator):
		self.__iterator=iterator

	def next(self):
		return variant(string(unicode(self.__iterator.next())))

class cookies_collection(generic):

	def __init__(self):
		pass

	def __call__(self, name, let=None, set=None):
		name=as_string(name)
		if let is not None:
			value=as_value(let).value
			if isinstance(value, str) or isinstance(value, unicode):
				cookies=src.request.request_manager.get_request().cookies().cookies()
				cookies[name]=value
			else:
				raise errors.type_mismatch
		elif set is not None:
			raise errors.object_has_no_property
		else:
			cookies=src.request.request_manager.get_request().cookies()
			return string(cookies[name]) if name in cookies else v_empty

	def __iter__(self):
		cookies=src.request.request_manager.get_request().cookies()
		return cookies_collection_iterator(iter(cookies))

class arguments_collection_iterator(object):

	def __init__(self, iterator):
		self.__iterator=iterator

	def next(self):
		return variant(string(unicode(self.__iterator.next())))

class arguments_collection(generic):

	def __init__(self):
		pass

	def __call__(self, name, let=None, set=None):
		name=as_string(name)
		if let is not None:
			raise errors.object_has_no_property
			#value=as_value(let).value
			#if isinstance(value, str) or isinstance(value, unicode):
			#	arguments=src.request.request_manager.get_request().arguments().arguments()
			#	arguments[name]=value
			#else:
			#	raise errors.type_mismatch
		elif set is not None:
			raise errors.object_has_no_property
		else:
			arguments=src.request.request_manager.get_request().arguments().arguments()
			try:
				return string(unicode(arguments[name][0].decode("utf-8"))) if name in arguments else v_empty
			except UnicodeDecodeError, error:
				return binary(arguments[name][0])

	def __iter__(self):
		arguments=src.request.request_manager.get_request().arguments().arguments()
		return arguments_collection_iterator(iter(arguments))

class servervariables_collection_iterator(object):

	def __init__(self, iterator):
		self.__iterator=iterator

	def next(self):
		return variant(string(unicode(self.__iterator.next())))

class servervariables_collection(generic):

	def __init__(self):
		pass

	def __call__(self, name, let=None, set=None):
		name=as_string(name).upper()
		if let is not None:
			raise errors.object_has_no_property
		elif set is not None:
			raise errors.object_has_no_property
		elif name.startswith(u"HEADER_"):
			return self.variable_header_any(name)
		elif name.startswith(u"HTTP_"):
			return self.variable_http_any(name)
		else:
			return self.variable_table[name](self)

	def __iter__(self):
		collection=[]
		for name in self.variable_table:
			collection.append(name)
		headers=src.request.request_manager.get_request().headers().headers()
		for name in headers:
			collection.append(u"HEADER_%s"%name)
		for name in headers:
			collection.append(u"HTTP_%s"%name.upper().replace(u"-", u"_"))
		return servervariables_collection_iterator(iter(collection))
	

	
	def variable_header_any(self, name):
		return string(unicode(src.request.request_manager.get_request().headers().headers()[name[7:]]))

	def variable_http_any(self, name):
		return string(unicode(src.request.request_manager.get_request().headers().headers()[name[5:].replace(u"_", u"-")]))
	

	
	def variable_all_http(self):
		return string(u"\n".join([u"HTTP_%s=%s"%(unicode(name.upper()).replace(u"-", u"_"), unicode(value)) \
			for name, value in src.request.request_manager.get_request().headers().headers().items()]))

	def variable_raw_http(self):
		return string(u"\n".join([u"%s=%s"%(unicode(name), unicode(value)) for name, value in \
			src.request.request_manager.get_request().headers().headers().items()]))

	def variable_auth_password(self):
		return v_empty

	def variable_auth_type(self):
		return string(u"Basic")

	def variable_auth_user(self):
		return string(unicode(src.request.request_manager.get_request().session().user))

	def variable_content_length(self):
		return v_empty

	def variable_content_type(self):
		return v_empty

	def variable_gateway_interface(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["GATEWAY_INTERFACE"]))

	def variable_local_addr(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["SERVER_ADDR"]))

	def variable_query_stirng(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["QUERY_STRING"]))

	def variable_remote_addr(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["REMOTE_ADDR"]))

	def variable_remote_host(self):
		return v_empty

	def variable_remote_port(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["REMOTE_PORT"]))

	def variable_remote_user(self):
		return string(unicode(src.request.request_manager.get_request().session().user))

	def variable_request_method(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["REQUEST_METHOD"]))

	def variable_script_name(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["SCRIPT_NAME"]))

	def variable_server_name(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["SERVER_NAME"]))

	def variable_server_port(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["SERVER_PORT"]))

	def variable_server_port_secure(self):
		return integer(0)

	def variable_server_protocol(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["SERVER_PROTOCOL"]))

	def variable_server_software(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["SERVER_SOFTWARE"]))

	def variable_unencoded_url(self):
		environment=src.request.request_manager.get_request().environment().environment()
		return string(unicode(environment["SCRIPT_NAME"]+environment["QUERY_STRING"]))

	def variable_script_name(self):
		return string(unicode(src.request.request_manager.get_request().environment().environment()["SCRIPT_NAME"]))


	
	variable_table={
		u"ALL_HTTP": variable_all_http,
		u"RAW_HTTP": variable_raw_http,
		u"AUTH_PASSWORD": variable_auth_password,
		u"AUTH_TYPE": variable_auth_type,
		u"AUTH_USER": variable_auth_user,
		u"CONTENT_LENGTH": variable_content_length,
		u"CONTENT_TYPE": variable_content_type,
		u"GATEWAY_INTERFACE": variable_gateway_interface,
		u"QUERY_STRING": variable_query_stirng,
		u"REMOTE_ADDR": variable_remote_addr,
		u"REMOTE_HOST": variable_remote_host,
		u"REMOTE_PORT": variable_remote_port,
		u"REMOTE_USER": variable_remote_user,
		u"REQUEST_METHOD": variable_request_method,
        u"SCRIPT_NAME": variable_script_name,
		u"SERVER_NAME": variable_server_name,
		u"SERVER_PORT": variable_server_port,
		u"SERVER_PORT_SECURE": variable_server_port_secure,
		u"SERVER_PROTOCOL": variable_server_protocol,
		u"SERVER_SOFTWARE": variable_server_software,
		u"UNENCODED_URL": variable_unencoded_url,
		u"SCRIPT_NAME": variable_script_name}

class request(generic):
	
	def __init__(self):
		self.v_cookies=cookies_collection()
		self.v_arguments=arguments_collection()
		self.v_form=self.v_arguments
		self.v_querystring=self.v_arguments
		self.v_servervariables=servervariables_collection()



request=request()
