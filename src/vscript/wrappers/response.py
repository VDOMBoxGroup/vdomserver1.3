
import managers #, object



request=None # TODO: TEMPORARY DUMMY



from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *
from .request import cookies_collection



class response(generic):

	def __init__(self):
		generic.__init__(self)
		self.v_cookies=cookies_collection()

	def v_addheader(self, name, value):
		name=as_string(name).lower()
		headers=managers.request_manager.get_request().headers_out().headers()
		if not name in headers:
			headers[name]=as_string(value)

	def v_redirect(self, url):
		object.request.redirect(as_string(url))

	def v_write(self, data):
		object.request.write(as_string(data))
	
	def v_isclientconnected(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property
		else:
			return boolean(v_true_value)



response=response()
