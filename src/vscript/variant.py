
import sys
from copy import deepcopy

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



class variant(object):

	def __init__(self, value=v_empty):
		self.value=value

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			if hasattr(self.value, "let"):
				value=self.value.let(*arguments, **keywords)
				if value is not None: # Hack to allow assign array to array and not only
					self.value=value
			else:
				if arguments:
					raise errors.type_mismatch
				self.value=as_value(keywords["let"])
		elif "set" in keywords:
			if hasattr(self.value, "set"):
				value=self.value.set(*arguments, **keywords)
				if value is not None: # Hack to allow assign array to array and not only
					self.value=value
			else:
				if arguments:
					raise errors.type_mismatch
				self.value=as_generic(keywords["set"])
		else:
			if hasattr(self.value, "get"):
				return self.value.get(*arguments, **keywords)
			else:
				return self.value(*arguments, **keywords)

	def __getattr__(self, name):
		if not isinstance(self.value, generic):
			raise errors.object_required
		try:
			return getattr(self.value, name)
		except AttributeError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.object_has_no_property(name), None, extraceback

	
	
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
		return "VARIANT@%s:%s"%(object.__repr__(self)[-9:-1], repr(self.value))



from auxiliary import as_value, as_is, as_array, as_integer, as_double, as_string, as_boolean, as_generic, as_date
