
import managers #, object
request=None # TODO: TEMPORARY DUMMY

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

from request import cookies_collection



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
