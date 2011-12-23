
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *



absent="absent"



def localpack(value):
	return value if isinstance(value, (empty, null, nothing, generic)) else pack(value)

def localunpack(value):
	return value if isinstance(value, (empty, null, nothing, generic)) else unpack(value)



class v_dictionary_iterator(generic):

	def __init__(self, iterator):
		self.iterator=iterator

	def next(self):
		return localpack(self.iterator.next())

class v_dictionary(generic):

	def __init__(self, values=None):
		generic.__init__(self)
		self.values=values or {}

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			self.let(*arguments, **keywords)
		elif "set" in keywords:
			self.set(*arguments, **keywords)
		else:
			# Experimental hack to simulate non-object behaviour
			# Allow both let and set assigment and pass as_value for example
			if arguments:
				return self.get(*arguments, **keywords)
			else:
				return self



	def get(self, key, *arguments, **keywords):
		if arguments:
			raise errors.wrong_number_of_arguments
		return self.values[localunpack(as_is(key))]

	def let(self, *arguments, **keywords):
		if not arguments:
			return keywords["set"]
		if len(arguments)>1:
			raise errors.wrong_number_of_arguments
		self.values[localunpack(as_is(arguments[0]))]=as_value(keywords["let"])

	def set(self, *arguments, **keywords):
		if not arguments:
			return keywords["set"]
		if len(arguments)>1:
			raise errors.wrong_number_of_arguments
		self.values[localunpack(as_is(arguments[0]))]=as_generic(keywords["set"])


	
	def erase(self):
		self.values.clear()

	
	
	def v_contains(self, key):
		return localunpack(as_is(key)) in self.values

	def v_extend(self, object, separator=None):
		object=as_array(object)
		if separator is None:
			separator=u" "
		if len(object.subscripts)>1:
			edge=len(object.subscripts)-1
			iterators=[None]*len(object.subscripts)
			iterators[edge]=-1, iter(object.values)
			level=edge
			while level<=edge:
				if level:
					try:
						index, iterator=iterators[level]
						array=iterator.next()
					except StopIteration:
						level+=1
					else:
						iterators[level]=index+1, iterator
						level-=1
						iterators[level]=-1, iter(array)
				else:
					index, iterator=iterators[level]
					indexes=separator.join(reversed([str(i1) for i1, i2 in iterators[1:]]))
					for index, item in enumerate(iterator):
						self.values[u"%s%s%s"%(index, separator, indexes)]=item
					level+=1
		else:
			for index, item in enumerate(object.values):
				self.values[u"%s"%index]=item
		
	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(len(self.values))

	def v_remove(self, key):
		del self.values[localunpack(as_is(key))]

	
	
	def __iter__(self):
		return v_dictionary_iterator(iter(self.values))


	
	def __len__(self):
		return len(self.values)

	def __nonzero__(self):
		return len(self.values)

	def __invert__(self):
		return len(self.values)==0
