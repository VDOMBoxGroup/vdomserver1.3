
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
from binary import binary



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

def as_array(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	if not isinstance(value, array):
		raise errors.type_mismatch
	return value

def as_integer(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return int(value)

def as_double(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return float(value)

def as_string(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return unicode(value)

def as_boolean(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if isinstance(value, generic):
		value=value()
	return bool(value)

def as_generic(value, specific=generic):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if not isinstance(value, specific):
		raise errors.object_required
	return value

def as_date(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if not isinstance(value, date):
		raise errors.object_required
	return value.value

def as_binary(value):
	if isinstance(value, (variant, constant, shadow)):
		value=value.value
	if not isinstance(value, binary):
		raise errors.object_required
	return value.value



def raise_type_mismatch_error(value):
	raise errors.type_mismatch

pack_table={
	int: lambda value:integer(value),
	str: lambda value:string(unicode(value)),
	unicode: lambda value:string(value),
	bool: lambda value:boolean(value),
	None: lambda value:v_null}

def pack(value):
	return pack_table.get(type(value), raise_type_mismatch_error)(value)

unpack_table={
	integer: lambda value:value.value,
	string: lambda value:value.value,
	boolean: lambda value:value.value,
	v_null: lambda value:None}

def unpack(value):
	return unpack_table.get(type(value), raise_type_mismatch_error)(value)



def adapt(arguments, adaptors, require=0, name=None):
	if len(arguments)<require or len(arguments)>len(adaptors):
		raise errors.wrong_number_of_arguments(name=name)
	return dict(((name, adaptor(argument)) \
		for (name, adaptor), argument in zip(adaptors, arguments)))



from variant import variant
from constant import constant
from shadow import shadow
