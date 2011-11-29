
import managers
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *



class session(generic):

	def __init__(self):
		generic.__init__(self)

	def v_abandon(self):
		raise errors.not_implemented

	def v_sessionid(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property
		else:
			return string(unicode(managers.request_manager.get_request().sid))

	def v_timeout(self, let=None, set=None):
		raise errors.not_implemented
		
	def v_variables(self, name, let=None, set=None):
		name=as_string(name)
		if let is not None:
			# managers.request_manager.get_request().session().value(name, value=as_string(let))
			managers.request_manager.get_request().session().value(name, value=let)
		elif set is not None:
			# raise errors.type_mismatch
			managers.request_manager.get_request().session().value(name, value=set)
		else:
			value=managers.request_manager.get_request().session().value(name)
			# return string(v_empty if value is None else value)
			return v_empty if value is None else value



session=session()
 