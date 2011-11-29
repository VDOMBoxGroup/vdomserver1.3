
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *



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
