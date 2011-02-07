
import errors, types

from generic import generic



class nothing(generic):

	def get_type_name(self):
		return "Nothing"

	
	
	def __copy__(self):
		return self

	def __deepcopy__(self, memo={}):
		return self



	def __repr__(self):
		return "NOTHING@%s"%object.__repr__(self)[-9:-1]



v_nothing=nothing()
