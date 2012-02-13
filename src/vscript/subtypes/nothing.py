
from .. import errors
from .generic import generic


class nothing(generic):

	name=property(lambda self: "Nothing")


	def __copy__(self):
		return self

	def __deepcopy__(self, memo={}):
		return self


	def __repr__(self):
		return "NOTHING@%08X"%id(self)


v_nothing=nothing()
