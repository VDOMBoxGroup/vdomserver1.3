
import managers
from ... import errors
from ...subtypes import boolean, generic, string, true, false, v_empty, v_mismatch
from ...variables import variant
from .request import v_cookiescollection


class v_response(generic):

	def v_cookies(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("cookies")
		else:
			return v_cookiescollection()
	
	def v_isclientconnected(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("isclientconnected")
		else:
			return boolean(true)

	def v_result(self, let=None, set=None):
		if let is not None:
			managers.request_manager.get_request().session().value("response", value=let.as_string)
		elif set is not None:
			raise errors.object_has_no_property("result")
		else:
			return string(managers.request_manager.get_request().session().value("response"))


	def v_addheader(self, name, value):
		managers.request_manager.get_request().headers_out().headers() \
			.setdefault(name.as_string.lower(), value.as_string)
		return v_mismatch

	def v_redirect(self, url):
		managers.request_manager.get_request().redirect(url.as_string)
		return v_mismatch

	def v_write(self, data):
		managers.request_manager.get_request().write(data.as_string)
		return v_mismatch


v_response=v_response()
