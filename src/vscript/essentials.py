
import types, random, re
from . import errors
from .primitives import subtype, variable
from .variables import variant


__all__=["check", "randomize", "echo", "concat", "exitloop", "exitdo", "exitfor"]


check_pattern=re.compile("(.+)\(\) (?:takes no arguments)|(?:takes exactly \d+ arguments) \(\d+ given\)")


subtype.byref=property(lambda self: variant(self))
subtype.byval=property(lambda self: variant(self.copy))
variable.byref=property(lambda self: self)
variable.byval=property(lambda self: variant(self.subtype.copy))


def check(value):
	if isinstance(value, (types.FunctionType, types.MethodType)):
		try:
			return value()
		except TypeError, error:
			match=check_pattern.search(error.message)
			if match: raise errors.wrong_number_of_arguments(name=match.group(1))
			else: raise
	else:
		return value


def randomize(seed=None):
	random.seed(seed)

def echo(*arguments):
	debug(" ".join([unicode(argument.as_simple) for argument in arguments]), console=True)

def concat(*arguments):
	return string(u"".join(unicode(argument.as_simple) for argument in arguments))


class exitloop(Exception):
	pass

class exitdo(exitloop):
	pass

class exitfor(exitloop):
	pass
