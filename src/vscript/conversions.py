
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


def as_is(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	return value

def as_value(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return value

def as_specific(value, specific):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if not isinstance(value, specific):
		raise errors.object_required
	return value


def as_array(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	if not isinstance(value, array):
		raise errors.type_mismatch
	return value

def as_binary(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if not isinstance(value, binary):
		raise errors.object_required
	return value.value

def as_boolean(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return bool(value)

def as_date(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if not isinstance(value, date):
		raise errors.object_required
	return value.value

def as_double(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return float(value)

def as_generic(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if not isinstance(value, generic):
		raise errors.object_required
	return value

def as_integer(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return int(value)

def as_string(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return unicode(value)


def type_mismatch_handler(value):
	raise errors.type_mismatch


pack_table={
	int: lambda value: integer(value),
	str: lambda value: string(unicode(value)),
	unicode: lambda value: string(value),
	bool: lambda value: boolean(value),
	float: lambda value: double(value),
	None: lambda value: v_null}

def pack(value):
	return pack_table.get(type(value), type_mismatch_handler)(value)

unpack_table={
	integer: lambda value: value.value,
	string: lambda value: value.value,
	binary: lambda value: value.value,
	boolean: lambda value: value.value,
	double: lambda value: value.value,
	v_null: lambda value: None}

def unpack(value):
	return unpack_table.get(type(value), type_mismatch_handler)(value)


from .variables.variant import variant
from .variables.constant import constant
from .variables.shadow import shadow
