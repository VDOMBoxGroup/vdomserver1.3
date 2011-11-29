
from copy import deepcopy
from .. import errors, types


class shadow(object):

	def __init__(self, owner=None, name=None):
		self.owner=owner
		self.name=name

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			setattr(self.owner, self.name, as_value(keywords["let"]))
		elif "set" in keywords:
			setattr(self.owner, self.name, as_generic(keywords["set"])) # as_value ???
		else:
			return getattr(self.owner, self.name)

	def __getattr__(self, name):
		return getattr(self.value, name)


	def get_value(self):
		return getattr(self.owner, self.name)

	value=property(get_value)


	def __iter__(self):
		return iter(self.value)


	def __add__(self, another):
		return self.value+another

	def __sub__(self, another):
		return self.value-another

	def __mul__(self, another):
		return self.value*another

	def __div__(self, another):
		return self.value/another

	def __floordiv__(self, another):
		return self.value//another

	def __mod__(self, another):
		return self.value%another

	def __pow__(self, another):
		return self.value**another


	def __eq__(self, another):
		return self.value==another

	def __ne__(self, another):
		return self.value!=another

	def __lt__(self, another):
		return self.value<another

	def __gt__(self, another):
		return self.value>another

	def __le__(self, another):
		return self.value<=another

	def __ge__(self, another):
		return self.value>=another

	def __hash__(self):
		return hash(self.value)


	def __and__(self, another):
		return self.value & another

	def __or__(self, another):
		return self.value | another

	def __xor__(self, another):
		return self.value ^ another


	def __invert__(self):
		return ~(self.value)
		
	def __neg__(self):
		return neg(self.value)

	def __pos__(self):
		return pos(self.value)

	def __abs__(self):
		return abs(self.value)


	def __int__(self):
		return int(self.value)

	def __float__(self):
		return float(self.value)

	def __str__(self):
		return str(self.value)

	def __unicode__(self):
		return unicode(self.value)

	def __nonzero__(self):
		return bool(self.value)


	def __repr__(self):
		return "SHADOW@%s:%s.%s"%(object.__repr__(self)[-9:-1], self.owner, self.name)


from ..conversions import as_value, as_generic
