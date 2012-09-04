
import managers
from ... import errors
from ...subtypes import integer, generic, string, v_empty, v_mismatch
from ...variables import variant


class v_cookiescollection(generic):

	def __call__(self, name, **keywords):
		if "let" in keywords:
			managers.request_manager.current.cookies()[name.as_string.encode("utf-8")]=keywords["let"].as_string.encode("utf-8")
		elif "set" in keywords:
			raise errors.object_has_no_property
		else:
			try:
				return string(managers.request_manager.current.cookies()[name.as_string.encode("utf-8")].value.decode("utf-8"))
			except KeyError:
				return v_empty


	def __iter__(self):
		for cookie in managers.request_manager.get_request().cookies().cookies():
			yield variant(string(unicode(cookie)))


class v_argumentscollection(generic):

	def __call__(self, name, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property
		else:
			try: value=managers.request_manager.get_request().arguments() \
				.arguments()[name.as_string][0]
			except KeyError: return v_empty
			
			try: 			
				if isinstance(value, str):
					return string(unicode(value.decode("utf-8", "ignore")))
				else:
					return string(unicode(value))
	
			except UnicodeDecodeError: 
				return binary(value)


	def __iter__(self):
		for argument in managers.request_manager.get_request().arguments().arguments():
			yield variant(string(unicode(argument)))


class v_servervariablescollection(generic):

	def __call__(self, name, **keywords):
		name=name.as_string.upper()
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property
		elif name.startswith(u"HEADER_"):
			return string(unicode(managers.request_manager.get_request().headers() \
				.headers()[name[7:]]))
		elif name.startswith(u"HTTP_"):
			return string(unicode(managers.request_manager.get_request().headers() \
				.headers()[name[5:].replace(u"_", u"-")]))
		else:
			return self.variable_table[name](self)


	variable_table={
		u"ALL_HTTP": lambda self: string(u"\n".join([u"HTTP_%s=%s"%(unicode(name.upper()) \
			.replace(u"-", u"_"), unicode(value)) for name, value in managers.request_manager \
			.get_request().headers().headers().items()])),
		u"RAW_HTTP": lambda self: string(u"\n".join([u"%s=%s"%(unicode(name), \
			unicode(value)) for name, value in managers.request_manager.get_request().headers() \
			.headers().items()])),
		u"AUTH_PASSWORD": lambda self: v_empty,
		u"AUTH_TYPE": lambda self: string(u"Basic"),
		u"AUTH_USER": lambda self: string(unicode(managers.request_manager.get_request().session().user)),
		u"CONTENT_LENGTH": lambda self: v_empty,
		u"CONTENT_TYPE": lambda self: v_empty,
		u"GATEWAY_INTERFACE": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["GATEWAY_INTERFACE"])),
		u"QUERY_STRING": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["QUERY_STRING"])),
		u"LOCAL_ADDR": lambda self: v_empty,
		u"REMOTE_ADDR": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["REMOTE_ADDR"])),
		u"REMOTE_HOST": lambda self: v_empty,
		u"REMOTE_PORT": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["REMOTE_PORT"])),
		u"REMOTE_USER": lambda self: string(unicode(managers.request_manager.get_request().session().user)),
		u"REQUEST_METHOD": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["REQUEST_METHOD"])),
        u"SCRIPT_NAME": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["SCRIPT_NAME"])),
		u"SERVER_NAME": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["SERVER_NAME"])),
		u"SERVER_PORT": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["SERVER_PORT"])),
		u"SERVER_PORT_SECURE": lambda self: integer(0),
		u"SERVER_PROTOCOL": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["SERVER_PROTOCOL"])),
		u"SERVER_SOFTWARE": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["SERVER_SOFTWARE"])),
		u"UNENCODED_URL": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["SCRIPT_NAME"]+managers.request_manager \
			.get_request().environment().environment()["QUERY_STRING"])),
		u"SCRIPT_NAME": lambda self: string(unicode(managers.request_manager \
			.get_request().environment().environment()["SCRIPT_NAME"]))}


	def __iter__(self):
		for name in self.variable_table:
			yield variant(string(unicode(name)))
		for name in managers.request_manager.get_request().headers().headers():
			yield variant(string(u"HEADER_%s"%name))
			yield variant(string(u"HTTP_%s"%name.upper().replace(u"-", u"_")))


class v_parameterscollection(generic):

	def __call__(self, index, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property
		else:
			try:
				index, parameters=index.as_integer, managers.request_manager \
					.get_request().arguments().arguments()["xml_data"][0]
				if isinstance(parameters, list): return string(unicode(parameters[index]))
				else: return v_empty if index else string(unicode(parameters))
			except KeyError:
				return v_empty


	def __iter__(self):
		try: parameters=managers.request_manager.get_request().arguments() \
			.arguments()["xml_data"][0]
		except KeyError: return
		if isinstance(parameters, list):
			for parameter in parameters: yield variant(string(unicode(parameter)))
		else:
			yield variant(string(unicode(parameters)))


class v_request(generic):

	def v_cookies(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("cookies")
			else:
				return v_cookiescollection()
		else:
			return v_cookiescollection()(name, **keywords)

	def v_arguments(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("arguments")
			else:
				return v_argumentscollection()
		else:
			return v_argumentscollection()(name, **keywords)

	def v_form(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("form")
			else:
				return v_argumentscollection()
		else:
			return v_argumentscollection()(name, **keywords)

	def v_querystring(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("querystring")
			else:
				return v_argumentscollection()
		else:
			return v_argumentscollection()(name, **keywords)

	def v_servervariables(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("servervariables")
			else:
				return v_servervariablescollection()
		else:
			return v_servervariablescollection()(name, **keywords)

	def v_parameters(self, index=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("parameters")
			else:
				return v_parameterscollection()
		else:
			return v_parameterscollection()(index, **keywords)
