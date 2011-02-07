
import sys

from copy import copy, deepcopy

import errors, types



def dim(subscripts):
	array=[v_empty]*(subscripts[0]+1)
	for subscript in subscripts[1:]:
		item=array
		array=[item]
		for index in range(subscript):
			array.append(deepcopy(item))
	return array

def redim(subarray, subscripts, index):
	subscript=subscripts[index]
	if index>0:
		if subscript!=len(subarray)-1:
			raise errors.subscript_out_of_range
		for element in subarray:
			redim(element, subscripts, index=index-1)
	else:
		if subscript<len(subarray):
			del subarray[subscript+1:]
		elif subscript>len(subarray):
			subarray.extend([v_empty]*(subscript+1-len(subarray)))

def erase(subarray, level):
	if level:
		for element in subarray:
			erase(element, level-1)
	else:
		subarray[:]=[v_empty]*len(subarray)

def count(subarray, subscripts=None):
	if subscripts is None:
		subscripts=[]
		count(subarray, subscripts)
		return subscripts
	else:
		subscripts.insert(0, len(subarray)-1)
		if subarray and isinstance(subarray[0], list):
			count(subarray[0], subscripts)



class array_iterator(object):

	def __init__(self, subscripts, values):
		self.subscripts=subscripts
		self.values=values
	
	def __iter__(self):
		return self.next()

	def next(self):
		edge=len(self.subscripts)-1
		iterators=[None]*len(self.subscripts)
		iterators[edge]=iter(self.values)
		level=edge
		while level<=edge:
			if level:
				try:
					array=iterators[level].next()
				except StopIteration:
					level+=1
				else:
					level-=1
					iterators[level]=iter(array)
			else:
				for item in iterators[level]:
					yield item
				level+=1

class array(object):

	def __init__(self, subscripts=None, values=None):
		if subscripts:
			self.subscripts=subscripts
			self.values=dim(subscripts)
			self.static=None
		elif values:
			self.subscripts=count(values)
			self.values=values
			self.static=None
		else:
			self.subscripts=[]
			self.values=[]
			self.static=None

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			self.let(*arguments, **keywords)
		elif "set" in keywords:
			self.set(*arguments, **keywords)
		else:
			return self.get(*arguments, **keywords)



	def get(self, *indexes, **keywords):
		if len(indexes)!=len(self.subscripts):
			raise errors.subscript_out_of_range
		try:
			result=self.values
			for index in reversed(indexes):
				result=result[as_integer(index)]
			return result
		except IndexError:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.subscript_out_of_range, None, extraceback

	def let(self, *indexes, **keywords):
		if not indexes:
			return keywords["let"]
		if len(indexes)!=len(self.subscripts):
			raise errors.subscript_out_of_range
		try:
			elements=self.values
			for index in indexes[-1:0:-1]:
				elements=elements[as_integer(index)]
			elements[as_integer(indexes[0])]=as_value(keywords["let"])
		except IndexError:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.subscript_out_of_range, None, extraceback

	def set(self, *indexes, **keywords):
		if not indexes:
			return keywords["set"]
		if len(indexes)!=len(self.subscripts):
			raise errors.subscript_out_of_range
		try:
			elements=self.values
			for index in indexes[-1:0:-1]:
				elements=elements[as_integer(index)]
			elements[as_integer(indexes[0])]=as_generic(keywords["set"])
		except IndexError:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.subscript_out_of_range, None, extraceback
	

	
	def get_type_code(self):
		return 8204

	def get_type_name(self):
		return "Array"



	dimension=property(lambda self: len(self.subscripts))

    

	def redim(self, subscripts, preserve=False):
		if self.static:
			raise errors.static_array
		if subscripts:
			subscripts=[as_integer(subscript) for subscript in subscripts]
			if preserve:
				redim(self.values, subscripts, len(subscripts)-1)
			else:
				self.values=dim(subscripts)
		else:
			self.values=[]
		self.subscripts=deepcopy(subscripts)

	def erase(self):
		if self.static:
			erase(self.values, len(self.subscripts)-1)
		else:
			del self.values[:]
			self.subscripts=[]



	def __iter__(self):
		return array_iterator(self.subscripts, self.values).next()



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
		return "ARRAY@%s:%s"%(object.__repr__(self)[-9:-1], list.__repr__(self.values))



from auxiliary import as_value, as_is, as_array, as_integer, as_double, as_string, as_boolean, as_generic, as_date

from empty import empty, v_empty
from variant import variant
