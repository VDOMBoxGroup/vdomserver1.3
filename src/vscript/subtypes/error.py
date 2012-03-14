
from .. import errors
from ..primitives import subtype


class error(subtype):

	def __init__(self, value):
		self._value=value


	value=property(lambda self: self._value)


	code=property(lambda self: 10)
	name=property(lambda self: "Error")


	as_simple=property(lambda self: self)


	def v_message(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property
		else:
			return string(unicode(str(self._value)))


	def __repr__(self):
		return "ERROR@%08X"%id(self)


from .string import string
