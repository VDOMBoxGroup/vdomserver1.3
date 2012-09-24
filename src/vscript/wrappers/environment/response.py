
import managers
from ... import errors
from ...subtypes import boolean, generic, string, true, false, v_empty, v_mismatch
from ...variables import variant
from .request import v_cookiescollection


class v_response(generic):

	def __init__(self):
		self._cookies=v_cookiescollection()


	def v_cookies(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("cookies")
			else:
				return self._cookies
		else:
			return self._cookies(name, **keywords)
	
	def v_isclientconnected(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("isclientconnected")
		else:
			return boolean(true)

	def v_result(self, **keywords):
		if "let" in keywords:
			managers.request_manager.current.session().value("response", value=keywords["let"].as_string)
		elif "set" in keywords:
			raise errors.object_has_no_property("result")
		else:
			return string(managers.request_manager.current.session().value("response"))


	def v_addheader(self, name, value):
		managers.request_manager.current.headers_out().headers() \
			.setdefault(name.as_string.lower(), value.as_string)
		return v_mismatch

	def v_redirect(self, url):
		managers.request_manager.current.redirect(url.as_string)
		return v_mismatch

	def v_write(self, data):
		managers.request_manager.current.write(data.as_string)
		return v_mismatch
