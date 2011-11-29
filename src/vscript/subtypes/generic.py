
from .. import errors, types


class generic(object):

	def __init__(self):
		pass

	def __call__(self, *arguments, **keywords):
		raise errors.object_has_no_property


	def get_type_code(self):
		return 9

	def get_type_name(self):
		return "Object"


	def __add__(self, another):
		raise errors.type_mismatch

	def __sub__(self, another):
		raise errors.type_mismatch

	def __mul__(self, another):
		raise errors.type_mismatch

	def __div__(self, another):
		raise errors.type_mismatch

	def __floordiv__(self, another):
		raise errors.type_mismatch

	def __mod__(self, another):
		raise errors.type_mismatch

	def __pow__(self, another):
		raise errors.type_mismatch


	def __eq__(self, another):
		raise errors.type_mismatch

	def __ne__(self, another):
		raise errors.type_mismatch

	def __lt__(self, another):
		raise errors.type_mismatch

	def __gt__(self, another):
		raise errors.type_mismatch

	def __le__(self, another):
		raise errors.type_mismatch

	def __ge__(self, another):
		raise errors.type_mismatch

	def __hash__(self):
		raise NotImplementedError


	def __and__(self, another):
		raise errors.type_mismatch

	def __or__(self, another):
		raise errors.type_mismatch

	def __xor__(self, another):
		raise errors.type_mismatch


	def __invert__(self):
		raise errors.type_mismatch
		
	def __neg__(self):
		raise errors.type_mismatch

	def __pos__(self):
		raise errors.type_mismatch

	def __abs__(self):
		raise errors.type_mismatch


	def __int__(self):
		raise errors.type_mismatch
		
	def __str__(self):
		raise errors.type_mismatch
		
	def __unicode__(self):
		raise errors.type_mismatch

	def __nonzero__(self):
		raise errors.type_mismatch


	def __repr__(self):
		return "GENERIC@%s"%object.__repr__(self)[-9:-1]
