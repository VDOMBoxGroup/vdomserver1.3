
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



class session(generic):

	def __init__(self):
		generic.__init__(self)

	def v_abandon(self):
		raise errors.not_implemented

	def v_sessionid(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property
		else:
			return string(unicode(src.request.request_manager.get_request().sid))

	def v_timeout(self, let=None, set=None):
		raise errors.not_implemented
		
	def v_variables(self, name, let=None, set=None):
		name=as_string(name)
		if let is not None:
			# src.request.request_manager.get_request().session().value(name, value=as_string(let))
			src.request.request_manager.get_request().session().value(name, value=let)
		elif set is not None:
			# raise errors.type_mismatch
			src.request.request_manager.get_request().session().value(name, value=set)
		else:
			value=src.request.request_manager.get_request().session().value(name)
			# return string(v_empty if value is None else value)
			return v_empty if value is None else value



session=session()
 