
from .. import errors
from ..primitives import variable


class shadow(variable):

	def __init__(self, owner=None, name=None):
		self._owner=owner
		self._name=name

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			if arguments:
				raise errors.type_mismatch
			else:
				setattr(self._owner, self._name, keywords["let"].as_simple)
		elif "set" in keywords:
			if arguments:
				raise errors.type_mismatch
			else:
				setattr(self._owner, self._name, keywords["let"].as_complex)
		else:
			raise errors.type_mismatch


	subtype=property(lambda self: getattr(self._owner, self._name).subtype)
	value=property(lambda self: getattr(self._owner, self._name).value)


	def __repr__(self):
		return "SHADOW@%08X:%s"%(id(self), repr(getattr(self._owner, self._name)))
