
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



class v_list_iterator(generic):

	def __init__(self, iterator):
		self.__iterator=iterator

	def next(self):
		return self.__iterator.next()

class v_list(generic):

	def __init__(self):
		generic.__init__(self)
		self.values=[]


	
	def erase(self):
		self.values.clear()

	
	
	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(len(self.values))

	def v_append(self, value):
		self.values.append(as_value(value))

	def v_insert(self, index, value):
		self.insert(as_integer(index), as_value(value))

	def v_remove(self, value):
		self.values.remove(as_value(value))

	def v_index(self, value):
		return self.values.index(as_value(value))

	def v_count(self, value):
		return self.values.count(as_value(value))

	def v_push(self, value):
		self.values.append(as_value(value))

	def v_pop(self):
		return self.values.pop()
		
	
	
	def __iter__(self):
		return v_list_iterator(iter(self.values))


	
	def __len__(self):
		return len(self.values)

	def __nonzero__(self):
		return len(self.values)

	def __invert__(self):
		return len(self.values)==0
