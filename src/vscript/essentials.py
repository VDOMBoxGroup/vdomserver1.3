
import random, re
from copy import copy, deepcopy
from . import errors, types
from .subtypes.array import array
from .subtypes.binary import binary
from .subtypes.boolean import boolean, v_true_value, v_false_value
from .subtypes.date import date
from .subtypes.double import double, nan, infinity
from .subtypes.empty import empty, v_empty
from .subtypes.error import error
from .subtypes.generic import generic
from .subtypes.integer import integer
from .subtypes.nothing import nothing, v_nothing
from .subtypes.null import null, v_null
from .subtypes.string import string
from .variables.variant import variant
from .variables.constant import constant
from .variables.shadow import shadow
from .conversions import as_value


__all__=["check", "byref", "byval", "redim", "erase", "randomize", "echo", "concat", "exitloop", "exitdo", "exitfor"]


def check(value):
	if isinstance(value, (types.function, types.method)):
		try:
			return value()
		except TypeError, error:
			result=re.search("(.+)\(\) (?:takes no arguments)|(?:takes exactly \d+ arguments) \(\d+ given\)", error.message)
			if result:
				raise errors.wrong_number_of_arguments(name=result.group(1))
			else:
				raise
	else:
		return value


def byref(value):
	if not isinstance(value, (variant, constant, shadow)):
		value=variant(value=value)
	return value

def byval(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	return variant(value=deepcopy(value))


def redim(variable, subscripts, preserve=False):
	if isinstance(variable, (variant, constant, shadow))\
		and hasattr(variable.value, "redim"):
		variable.value.redim(as_value(subscripts), preserve=preserve)
	else:
		raise errors.type_mismatch

def erase(variable):
	if isinstance(variable, (variant, constant, shadow))\
		and hasattr(variable.value, "erase"):
		variable.value.erase()
	else:
		raise errors.type_mismatch


def randomize(seed=None):
	random.seed(seed)

def echo(*arguments):
	debug(" ".join([unicode(as_value(argument)) for argument in arguments]), console=True)

def concat(*arguments):
	return string(u"".join(unicode(argument) for argument in arguments))


class exitloop(Exception):
	pass

class exitdo(exitloop):
	pass

class exitfor(exitloop):
	pass
