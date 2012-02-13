
import managers
from ... import errors
from ...primitives import subtype
from ...subtypes import generic, string, v_empty


class v_session(generic):

	def v_sessionid(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("sessionid")
		else:
			return string(unicode(managers.request_manager.get_request().sid))

	def v_timeout(self, let=None, set=None):
		raise errors.not_implemented
		
	def v_variables(self, name, let=None, set=None):
		name=name.as_string
		if let is not None:
			managers.request_manager.get_request().session().value(name, value=let.as_is)
		elif set is not None:
			managers.request_manager.get_request().session().value(name, value=let.as_is)
		else:
			value=managers.request_manager.get_request().session().value(name)
			if isinstance(value, subtype):
				return value
			elif value is None:
				return v_empty
			else:
				raise errors.type_mismatch


	def v_abandon(self):
		raise errors.not_implemented


v_session=v_session()
