
from copy import copy, deepcopy

import random, re

import util.exception

import options, errors, types

from array import array
from empty import empty, v_empty
from null import null, v_null
from integer import integer
from double import double, nan, infinity
from date import date
from string import string
from boolean import boolean, v_true_value, v_false_value
from generic import generic
from error import error
from nothing import nothing, v_nothing
from variant import variant
from constant import constant
from shadow import shadow

import auxiliary



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
		variable.value.redim(auxiliary.as_value(subscripts), preserve=preserve)
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
	debug(" ".join([unicode(auxiliary.as_value(argument)) for argument in arguments]), console=True)

#def concat(value1, value2):
#	return unicode(value1)+unicode(value2)

def concat(*arguments):
	return string(u"".join(unicode(argument) for argument in arguments))



class exitloop(Exception):
	pass

class exitdo(exitloop):
	pass

class exitfor(exitloop):
	pass



empty.add_table={
	empty: empty.add_empty,
	null: empty.with_null,
	integer: empty.add_integer,
	double: empty.add_double,
	date: empty.add_date,
	string: empty.add_string,
	boolean: empty.add_boolean,
	variant: empty.add_variant,
	constant: empty.add_variant,
	shadow: empty.add_variant}

empty.sub_table={
	empty: empty.sub_empty,
	null: empty.with_null,
	integer: empty.sub_integer,
	double: empty.sub_double,
	date: empty.sub_date,
	string: empty.sub_string,
	boolean: empty.sub_boolean,
	variant: empty.sub_variant,
	constant: empty.sub_variant,
	shadow: empty.sub_variant}

empty.mul_table={
	empty: empty.mul_empty,
	null: empty.with_null,
	integer: empty.mul_integer,
	double: empty.mul_double,
	date: empty.mul_date,
	string: empty.mul_string,
	boolean: empty.mul_boolean,
	variant: empty.mul_variant,
	constant: empty.mul_variant,
	shadow: empty.mul_variant}

empty.div_table={
	empty: empty.div_empty,
	null: empty.with_null,
	integer: empty.div_integer,
	double: empty.div_double,
	date: empty.div_date,
	string: empty.div_string,
	boolean: empty.div_boolean,
	variant: empty.div_variant,
	constant: empty.div_variant,
	shadow: empty.div_variant}

empty.floordiv_table={
	empty: empty.floordiv_empty,
	null: empty.with_null,
	integer: empty.floordiv_integer,
	double: empty.floordiv_double,
	date: empty.floordiv_date,
	string: empty.floordiv_string,
	boolean: empty.floordiv_boolean,
	variant: empty.floordiv_variant,
	constant: empty.floordiv_variant,
	shadow: empty.floordiv_variant}

empty.mod_table={
	empty: empty.mod_empty,
	null: empty.with_null,
	integer: empty.mod_integer,
	double: empty.mod_double,
	date: empty.mod_date,
	string: empty.mod_string,
	boolean: empty.mod_boolean,
	variant: empty.mod_variant,
	constant: empty.mod_variant,
	shadow: empty.mod_variant}

empty.pow_table={
	empty: empty.pow_empty,
	null: empty.with_null,
	integer: empty.pow_integer,
	double: empty.pow_double,
	date: empty.pow_date,
	string: empty.pow_string,
	boolean: empty.pow_boolean,
	variant: empty.pow_variant,
	constant: empty.pow_variant,
	shadow: empty.pow_variant}



empty.eq_table={
	empty: empty.eq_empty,
	null: empty.with_null,
	integer: empty.eq_integer,
	double: empty.eq_double,
	date: empty.eq_date,
	string: empty.eq_string,
	boolean: empty.eq_boolean,
	variant: empty.eq_variant,
	constant: empty.eq_variant,
	shadow: empty.eq_variant}

empty.ne_table={
	empty: empty.ne_empty,
	null: empty.with_null,
	integer: empty.ne_integer,
	double: empty.ne_double,
	date: empty.ne_date,
	string: empty.ne_string,
	boolean: empty.ne_boolean,
	variant: empty.ne_variant,
	constant: empty.ne_variant,
	shadow: empty.ne_variant}

empty.lt_table={
	empty: empty.lt_empty,
	null: empty.with_null,
	integer: empty.lt_integer,
	double: empty.lt_double,
	date: empty.lt_date,
	string: empty.lt_string,
	boolean: empty.lt_boolean,
	variant: empty.lt_variant,
	constant: empty.lt_variant,
	shadow: empty.lt_variant}

empty.gt_table={
	empty: empty.gt_empty,
	null: empty.with_null,
	integer: empty.gt_integer,
	double: empty.gt_double,
	date: empty.gt_date,
	string: empty.gt_string,
	boolean: empty.gt_boolean,
	variant: empty.gt_variant,
	constant: empty.gt_variant,
	shadow: empty.gt_variant}

empty.le_table={
	empty: empty.le_empty,
	null: empty.with_null,
	integer: empty.le_integer,
	double: empty.le_double,
	date: empty.le_date,
	string: empty.le_string,
	boolean: empty.le_boolean,
	variant: empty.le_variant,
	constant: empty.le_variant,
	shadow: empty.le_variant}

empty.ge_table={
	empty: empty.ge_empty,
	null: empty.with_null,
	integer: empty.ge_integer,
	double: empty.ge_double,
	date: empty.ge_date,
	string: empty.ge_string,
	boolean: empty.ge_boolean,
	variant: empty.ge_variant,
	constant: empty.ge_variant,
	shadow: empty.ge_variant}



empty.and_table={
	empty: empty.and_empty,
	null: empty.and_null,
	integer: empty.and_integer,
	double: empty.and_double,
	date: empty.and_date,
	string: empty.and_string,
	boolean: empty.and_boolean,
	variant: empty.and_variant,
	constant: empty.and_variant,
	shadow: empty.and_variant}

empty.or_table={
	empty: empty.or_empty,
	null: empty.or_null,
	integer: empty.or_integer,
	double: empty.or_double,
	date: empty.or_date,
	string: empty.or_string,
	boolean: empty.or_boolean,
	variant: empty.or_variant,
	constant: empty.or_variant,
	shadow: empty.or_variant}

empty.xor_table={
	empty: empty.xor_empty,
	null: empty.xor_null,
	integer: empty.xor_integer,
	double: empty.xor_double,
	date: empty.xor_date,
	string: empty.xor_string,
	boolean: empty.xor_boolean,
	variant: empty.xor_variant,
	constant: empty.xor_variant,
	shadow: empty.xor_variant}



null.add_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.add_variant,
	constant: null.add_variant,
	shadow: null.add_variant}

null.sub_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.sub_variant,
	constant: null.sub_variant,
	shadow: null.sub_variant}

null.mul_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.mul_variant,
	constant: null.mul_variant,
	shadow: null.mul_variant}

null.div_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.div_variant,
	constant: null.div_variant,
	shadow: null.div_variant}

null.floordiv_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.floordiv_variant,
	constant: null.floordiv_variant,
	shadow: null.floordiv_variant}

null.mod_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.mod_variant,
	constant: null.mod_variant,
	shadow: null.mod_variant}

null.pow_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.pow_variant,
	constant: null.pow_variant,
	shadow: null.pow_variant}



null.eq_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.eq_variant,
	constant: null.eq_variant,
	shadow: null.eq_variant}

null.ne_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.ne_variant,
	constant: null.ne_variant,
	shadow: null.ne_variant}

null.lt_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.lt_variant,
	constant: null.lt_variant,
	shadow: null.lt_variant}

null.gt_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.gt_variant,
	constant: null.gt_variant,
	shadow: null.gt_variant}

null.le_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.le_variant,
	constant: null.le_variant,
	shadow: null.le_variant}

null.ge_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.with_null,
	variant: null.ge_variant,
	constant: null.ge_variant,
	shadow: null.ge_variant}



null.and_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.and_boolean,
	variant: null.and_variant,
	constant: null.and_variant,
	shadow: null.and_variant}

null.or_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.or_boolean,
	variant: null.or_variant,
	constant: null.or_variant,
	shadow: null.or_variant}

null.xor_table={
	empty: null.with_null,
	null: null.with_null,
	integer: null.with_null,
	double: null.with_null,
	date: null.with_null,
	string: null.with_null,
	boolean: null.xor_boolean,
	variant: null.xor_variant,
	constant: null.xor_variant,
	shadow: null.xor_variant}



integer.add_table={
	empty: integer.add_empty,
	null: integer.with_null,
	integer: integer.add_integer,
	double: integer.add_double,
	date: integer.add_date,
	string: integer.add_string,
	boolean: integer.add_boolean,
	variant: integer.add_variant,
	constant: integer.add_variant,
	shadow: integer.add_variant}

integer.sub_table={
	empty: integer.sub_empty,
	null: integer.with_null,
	integer: integer.sub_integer,
	double: integer.sub_double,
	date: integer.sub_date,
	string: integer.sub_string,
	boolean: integer.sub_boolean,
	variant: integer.sub_variant,
	constant: integer.sub_variant,
	shadow: integer.sub_variant}

integer.mul_table={
	empty: integer.mul_empty,
	null: integer.with_null,
	integer: integer.mul_integer,
	double: integer.mul_double,
	date: integer.mul_date,
	string: integer.mul_string,
	boolean: integer.mul_boolean,
	variant: integer.mul_variant,
	constant: integer.mul_variant,
	shadow: integer.mul_variant}

integer.div_table={
	empty: integer.div_empty,
	null: integer.with_null,
	integer: integer.div_integer,
	double: integer.div_double,
	date: integer.div_date,
	string: integer.div_string,
	boolean: integer.div_boolean,
	variant: integer.div_variant,
	constant: integer.div_variant,
	shadow: integer.div_variant}

integer.floordiv_table={
	empty: integer.floordiv_empty,
	null: integer.with_null,
	integer: integer.floordiv_integer,
	double: integer.floordiv_double,
	date: integer.floordiv_date,
	string: integer.floordiv_string,
	boolean: integer.floordiv_boolean,
	variant: integer.floordiv_variant,
	constant: integer.floordiv_variant,
	shadow: integer.floordiv_variant}

integer.mod_table={
	empty: integer.mod_empty,
	null: integer.with_null,
	integer: integer.mod_integer,
	double: integer.mod_double,
	date: integer.mod_date,
	string: integer.mod_string,
	boolean: integer.mod_boolean,
	variant: integer.mod_variant,
	constant: integer.mod_variant,
	shadow: integer.mod_variant}

integer.pow_table={
	empty: integer.pow_empty,
	null: integer.with_null,
	integer: integer.pow_integer,
	double: integer.pow_double,
	date: integer.pow_date,
	string: integer.pow_string,
	boolean: integer.pow_boolean,
	variant: integer.pow_variant,
	constant: integer.pow_variant,
	shadow: integer.pow_variant}



integer.eq_table={
	empty: integer.eq_empty,
	null: integer.with_null,
	integer: integer.eq_integer,
	double: integer.eq_double,
	date: integer.eq_date,
	string: integer.eq_string,
	boolean: integer.eq_boolean,
	variant: integer.eq_variant,
	constant: integer.eq_variant,
	shadow: integer.eq_variant}

integer.ne_table={
	empty: integer.ne_empty,
	null: integer.with_null,
	integer: integer.ne_integer,
	double: integer.ne_double,
	date: integer.ne_date,
	string: integer.ne_string,
	boolean: integer.ne_boolean,
	variant: integer.ne_variant,
	constant: integer.ne_variant,
	shadow: integer.ne_variant}

integer.lt_table={
	empty: integer.lt_empty,
	null: integer.with_null,
	integer: integer.lt_integer,
	double: integer.lt_double,
	date: integer.lt_date,
	string: integer.lt_string,
	boolean: integer.lt_boolean,
	variant: integer.lt_variant,
	constant: integer.lt_variant,
	shadow: integer.lt_variant}

integer.gt_table={
	empty: integer.gt_empty,
	null: integer.with_null,
	integer: integer.gt_integer,
	double: integer.gt_double,
	date: integer.gt_date,
	string: integer.gt_string,
	boolean: integer.gt_boolean,
	variant: integer.gt_variant,
	constant: integer.gt_variant,
	shadow: integer.gt_variant}

integer.le_table={
	empty: integer.le_empty,
	null: integer.with_null,
	integer: integer.le_integer,
	double: integer.le_double,
	date: integer.le_date,
	string: integer.le_string,
	boolean: integer.le_boolean,
	variant: integer.le_variant,
	constant: integer.le_variant,
	shadow: integer.le_variant}

integer.ge_table={
	empty: integer.ge_empty,
	null: integer.with_null,
	integer: integer.ge_integer,
	double: integer.ge_double,
	date: integer.ge_date,
	string: integer.ge_string,
	boolean: integer.ge_boolean,
	variant: integer.ge_variant,
	constant: integer.ge_variant,
	shadow: integer.ge_variant}



integer.and_table={
	empty: integer.and_empty,
	null: integer.and_null,
	integer: integer.and_integer,
	double: integer.and_double,
	date: integer.and_date,
	string: integer.and_string,
	boolean: integer.and_boolean,
	variant: integer.and_variant,
	constant: integer.and_variant,
	shadow: integer.and_variant}

integer.or_table={
	empty: integer.or_empty,
	null: integer.or_null,
	integer: integer.or_integer,
	double: integer.or_double,
	date: integer.or_date,
	string: integer.or_string,
	boolean: integer.or_boolean,
	variant: integer.or_variant,
	constant: integer.or_variant,
	shadow: integer.or_variant}

integer.xor_table={
	empty: integer.xor_empty,
	null: integer.xor_null,
	integer: integer.xor_integer,
	double: integer.xor_double,
	date: integer.xor_date,
	string: integer.xor_string,
	boolean: integer.xor_boolean,
	variant: integer.xor_variant,
	constant: integer.xor_variant,
	shadow: integer.xor_variant}



double.add_table={
	empty: double.add_empty,
	null: double.with_null,
	integer: double.add_integer,
	double: double.add_double,
	date: double.add_date,
	string: double.add_string,
	boolean: double.add_boolean,
	variant: double.add_variant,
	constant: double.add_variant,
	shadow: double.add_variant}

double.sub_table={
	empty: double.sub_empty,
	null: double.with_null,
	integer: double.sub_integer,
	double: double.sub_double,
	date: double.sub_date,
	string: double.sub_string,
	boolean: double.sub_boolean,
	variant: double.sub_variant,
	constant: double.sub_variant,
	shadow: double.sub_variant}

double.mul_table={
	empty: double.mul_empty,
	null: double.with_null,
	integer: double.mul_integer,
	double: double.mul_double,
	date: double.mul_date,
	string: double.mul_string,
	boolean: double.mul_boolean,
	variant: double.mul_variant,
	constant: double.mul_variant,
	shadow: double.mul_variant}

double.div_table={
	empty: double.div_empty,
	null: double.with_null,
	integer: double.div_integer,
	double: double.div_double,
	date: double.div_date,
	string: double.div_string,
	boolean: double.div_boolean,
	variant: double.div_variant,
	constant: double.div_variant,
	shadow: double.div_variant}

double.floordiv_table={
	empty: double.floordiv_empty,
	null: double.with_null,
	integer: double.floordiv_integer,
	double: double.floordiv_double,
	date: double.floordiv_date,
	string: double.floordiv_string,
	boolean: double.floordiv_boolean,
	variant: double.floordiv_variant,
	constant: double.floordiv_variant,
	shadow: double.floordiv_variant}

double.mod_table={
	empty: double.mod_empty,
	null: double.with_null,
	integer: double.mod_integer,
	double: double.mod_double,
	date: double.mod_date,
	string: double.mod_string,
	boolean: double.mod_boolean,
	variant: double.mod_variant,
	constant: double.mod_variant,
	shadow: double.mod_variant}

double.pow_table={
	empty: double.pow_empty,
	null: double.with_null,
	integer: double.pow_integer,
	double: double.pow_double,
	date: double.pow_date,
	string: double.pow_string,
	boolean: double.pow_boolean,
	variant: double.pow_variant,
	constant: double.pow_variant,
	shadow: double.pow_variant}



double.eq_table={
	empty: double.eq_empty,
	null: double.with_null,
	integer: double.eq_integer,
	double: double.eq_double,
	date: double.eq_date,
	string: double.eq_string,
	boolean: double.eq_boolean,
	variant: double.eq_variant,
	constant: double.eq_variant,
	shadow: double.eq_variant}

double.ne_table={
	empty: double.ne_empty,
	null: double.with_null,
	integer: double.ne_integer,
	double: double.ne_double,
	date: double.ne_date,
	string: double.ne_string,
	boolean: double.ne_boolean,
	variant: double.ne_variant,
	constant: double.ne_variant,
	shadow: double.ne_variant}

double.lt_table={
	empty: double.lt_empty,
	null: double.with_null,
	integer: double.lt_integer,
	double: double.lt_double,
	date: double.lt_date,
	string: double.lt_string,
	boolean: double.lt_boolean,
	variant: double.lt_variant,
	constant: double.lt_variant,
	shadow: double.lt_variant}

double.gt_table={
	empty: double.gt_empty,
	null: double.with_null,
	integer: double.gt_integer,
	double: double.gt_double,
	date: double.gt_date,
	string: double.gt_string,
	boolean: double.gt_boolean,
	variant: double.gt_variant,
	constant: double.gt_variant,
	shadow: double.gt_variant}

double.le_table={
	empty: double.le_empty,
	null: double.with_null,
	integer: double.le_integer,
	double: double.le_double,
	date: double.le_date,
	string: double.le_string,
	boolean: double.le_boolean,
	variant: double.le_variant,
	constant: double.le_variant,
	shadow: double.le_variant}

double.ge_table={
	empty: double.ge_empty,
	null: double.with_null,
	integer: double.ge_integer,
	double: double.ge_double,
	date: double.ge_date,
	string: double.ge_string,
	boolean: double.ge_boolean,
	variant: double.ge_variant,
	constant: double.ge_variant,
	shadow: double.ge_variant}



double.and_table={
	empty: double.and_empty,
	null: double.and_null,
	integer: double.and_integer,
	double: double.and_double,
	date: double.and_date,
	string: double.and_string,
	boolean: double.and_boolean,
	variant: double.and_variant,
	constant: double.and_variant,
	shadow: double.and_variant}

double.or_table={
	empty: double.or_empty,
	null: double.or_null,
	integer: double.or_integer,
	double: double.or_double,
	date: double.or_date,
	string: double.or_string,
	boolean: double.or_boolean,
	variant: double.or_variant,
	constant: double.or_variant,
	shadow: double.or_variant}

double.xor_table={
	empty: double.xor_empty,
	null: double.xor_null,
	integer: double.xor_integer,
	double: double.xor_double,
	date: double.xor_date,
	string: double.xor_string,
	boolean: double.xor_boolean,
	variant: double.xor_variant,
	constant: double.xor_variant,
	shadow: double.xor_variant}



date.add_table={
	empty: date.add_empty,
	null: date.with_null,
	integer: date.add_integer,
	double: date.add_double,
	date: date.add_date,
	string: date.add_string,
	boolean: date.add_boolean,
	variant: date.add_variant,
	constant: date.add_variant,
	shadow: date.add_variant}

date.sub_table={
	empty: date.sub_empty,
	null: date.with_null,
	integer: date.sub_integer,
	double: date.sub_double,
	date: date.sub_date,
	string: date.sub_string,
	boolean: date.sub_boolean,
	variant: date.sub_variant,
	constant: date.sub_variant,
	shadow: date.sub_variant}

date.mul_table={
	empty: date.mul_empty,
	null: date.with_null,
	integer: date.mul_integer,
	double: date.mul_double,
	date: date.mul_date,
	string: date.mul_string,
	boolean: date.mul_boolean,
	variant: date.mul_variant,
	constant: date.mul_variant,
	shadow: date.mul_variant}

date.div_table={
	empty: date.div_empty,
	null: date.with_null,
	integer: date.div_integer,
	double: date.div_double,
	date: date.div_date,
	string: date.div_string,
	boolean: date.div_boolean,
	variant: date.div_variant,
	constant: date.div_variant,
	shadow: date.div_variant}

date.floordiv_table={
	empty: date.floordiv_empty,
	null: date.with_null,
	integer: date.floordiv_integer,
	double: date.floordiv_double,
	date: date.floordiv_date,
	string: date.floordiv_string,
	boolean: date.floordiv_boolean,
	variant: date.floordiv_variant,
	constant: date.floordiv_variant,
	shadow: date.floordiv_variant}

date.mod_table={
	empty: date.mod_empty,
	null: date.with_null,
	integer: date.mod_integer,
	double: date.mod_double,
	date: date.mod_date,
	string: date.mod_string,
	boolean: date.mod_boolean,
	variant: date.mod_variant,
	constant: date.mod_variant,
	shadow: date.mod_variant}

date.pow_table={
	empty: date.pow_empty,
	null: date.with_null,
	integer: date.pow_integer,
	double: date.pow_double,
	date: date.pow_date,
	string: date.pow_string,
	boolean: date.pow_boolean,
	variant: date.pow_variant,
	constant: date.pow_variant,
	shadow: date.pow_variant}



date.eq_table={
	empty: date.eq_empty,
	null: date.with_null,
	integer: date.eq_integer,
	double: date.eq_double,
	date: date.eq_date,
	string: date.eq_string,
	boolean: date.eq_boolean,
	variant: date.eq_variant,
	constant: date.eq_variant,
	shadow: date.eq_variant}

date.ne_table={
	empty: date.ne_empty,
	null: date.with_null,
	integer: date.ne_integer,
	double: date.ne_double,
	date: date.ne_date,
	string: date.ne_string,
	boolean: date.ne_boolean,
	variant: date.ne_variant,
	constant: date.ne_variant,
	shadow: date.ne_variant}

date.lt_table={
	empty: date.lt_empty,
	null: date.with_null,
	integer: date.lt_integer,
	double: date.lt_double,
	date: date.lt_date,
	string: date.lt_string,
	boolean: date.lt_boolean,
	variant: date.lt_variant,
	constant: date.lt_variant,
	shadow: date.lt_variant}

date.gt_table={
	empty: date.gt_empty,
	null: date.with_null,
	integer: date.gt_integer,
	double: date.gt_double,
	date: date.gt_date,
	string: date.gt_string,
	boolean: date.gt_boolean,
	variant: date.gt_variant,
	constant: date.gt_variant,
	shadow: date.gt_variant}

date.le_table={
	empty: date.le_empty,
	null: date.with_null,
	integer: date.le_integer,
	double: date.le_double,
	date: date.le_date,
	string: date.le_string,
	boolean: date.le_boolean,
	variant: date.le_variant,
	constant: date.le_variant,
	shadow: date.le_variant}

date.ge_table={
	empty: date.ge_empty,
	null: date.with_null,
	integer: date.ge_integer,
	double: date.ge_double,
	date: date.ge_date,
	string: date.ge_string,
	boolean: date.ge_boolean,
	variant: date.ge_variant,
	constant: date.ge_variant,
	shadow: date.ge_variant}



date.and_table={
	empty: date.and_empty,
	null: date.and_null,
	integer: date.and_integer,
	double: date.and_double,
	date: date.and_date,
	string: date.and_string,
	boolean: date.and_boolean,
	variant: date.and_variant,
	constant: date.and_variant,
	shadow: date.and_variant}

date.or_table={
	empty: date.or_empty,
	null: date.or_null,
	integer: date.or_integer,
	double: date.or_double,
	date: date.or_date,
	string: date.or_string,
	boolean: date.or_boolean,
	variant: date.or_variant,
	constant: date.or_variant,
	shadow: date.or_variant}

date.xor_table={
	empty: date.xor_empty,
	null: date.xor_null,
	integer: date.xor_integer,
	double: date.xor_double,
	date: date.xor_date,
	string: date.xor_string,
	boolean: date.xor_boolean,
	variant: date.xor_variant,
	constant: date.xor_variant,
	shadow: date.xor_variant}



string.add_table={
	empty: string.add_empty,
	null: string.with_null,
	integer: string.add_integer,
	double: string.add_double,
	date: string.add_date,
	string: string.add_string,
	boolean: string.add_boolean,
	variant: string.add_variant,
	constant: string.add_variant,
	shadow: string.add_variant}

string.sub_table={
	empty: string.sub_empty,
	null: string.with_null,
	integer: string.sub_integer,
	double: string.sub_double,
	date: string.sub_date,
	string: string.sub_string,
	boolean: string.sub_boolean,
	variant: string.sub_variant,
	constant: string.sub_variant,
	shadow: string.sub_variant}

string.mul_table={
	empty: string.mul_empty,
	null: string.with_null,
	integer: string.mul_integer,
	double: string.mul_double,
	date: string.mul_date,
	string: string.mul_string,
	boolean: string.mul_boolean,
	variant: string.mul_variant,
	constant: string.mul_variant,
	shadow: string.mul_variant}

string.div_table={
	empty: string.div_empty,
	null: string.with_null,
	integer: string.div_integer,
	double: string.div_double,
	date: string.div_date,
	string: string.div_string,
	boolean: string.div_boolean,
	variant: string.div_variant,
	constant: string.div_variant,
	shadow: string.div_variant}

string.floordiv_table={
	empty: string.floordiv_empty,
	null: string.with_null,
	integer: string.floordiv_integer,
	double: string.floordiv_double,
	date: string.floordiv_date,
	string: string.floordiv_string,
	boolean: string.floordiv_boolean,
	variant: string.floordiv_variant,
	constant: string.floordiv_variant,
	shadow: string.floordiv_variant}

string.mod_table={
	empty: string.mod_empty,
	null: string.with_null,
	integer: string.mod_integer,
	double: string.mod_double,
	date: string.mod_date,
	string: string.mod_string,
	boolean: string.mod_boolean,
	variant: string.mod_variant,
	constant: string.mod_variant,
	shadow: string.mod_variant}

string.pow_table={
	empty: string.pow_empty,
	null: string.with_null,
	integer: string.pow_integer,
	double: string.pow_double,
	date: string.pow_date,
	string: string.pow_string,
	boolean: string.pow_boolean,
	variant: string.pow_variant,
	constant: string.pow_variant,
	shadow: string.pow_variant}



string.eq_table={
	empty: string.eq_empty,
	null: string.with_null,
	integer: string.eq_integer,
	double: string.eq_double,
	date: string.eq_date,
	string: string.eq_string,
	boolean: string.eq_boolean,
	variant: string.eq_variant,
	constant: string.eq_variant,
	shadow: string.eq_variant}

string.ne_table={
	empty: string.ne_empty,
	null: string.with_null,
	integer: string.ne_integer,
	double: string.ne_double,
	date: string.ne_date,
	string: string.ne_string,
	boolean: string.ne_boolean,
	variant: string.ne_variant,
	constant: string.ne_variant,
	shadow: string.ne_variant}

string.lt_table={
	empty: string.lt_empty,
	null: string.with_null,
	integer: string.lt_integer,
	double: string.lt_double,
	date: string.lt_date,
	string: string.lt_string,
	boolean: string.lt_boolean,
	variant: string.lt_variant,
	constant: string.lt_variant,
	shadow: string.lt_variant}

string.gt_table={
	empty: string.gt_empty,
	null: string.with_null,
	integer: string.gt_integer,
	double: string.gt_double,
	date: string.gt_date,
	string: string.gt_string,
	boolean: string.gt_boolean,
	variant: string.gt_variant,
	constant: string.gt_variant,
	shadow: string.gt_variant}

string.le_table={
	empty: string.le_empty,
	null: string.with_null,
	integer: string.le_integer,
	double: string.le_double,
	date: string.le_date,
	string: string.le_string,
	boolean: string.le_boolean,
	variant: string.le_variant,
	constant: string.le_variant,
	shadow: string.le_variant}

string.ge_table={
	empty: string.ge_empty,
	null: string.with_null,
	integer: string.ge_integer,
	double: string.ge_double,
	date: string.ge_date,
	string: string.ge_string,
	boolean: string.ge_boolean,
	variant: string.ge_variant,
	constant: string.ge_variant,
	shadow: string.ge_variant}



string.and_table={
	empty: string.and_empty,
	null: string.and_null,
	integer: string.and_integer,
	double: string.and_double,
	date: string.and_date,
	string: string.and_string,
	boolean: string.and_boolean,
	variant: string.and_variant,
	constant: string.and_variant,
	shadow: string.and_variant}

string.or_table={
	empty: string.or_empty,
	null: string.or_null,
	integer: string.or_integer,
	double: string.or_double,
	date: string.or_date,
	string: string.or_string,
	boolean: string.or_boolean,
	variant: string.or_variant,
	constant: string.or_variant,
	shadow: string.or_variant}

string.xor_table={
	empty: string.xor_empty,
	null: string.xor_null,
	integer: string.xor_integer,
	double: string.xor_double,
	date: string.xor_date,
	string: string.xor_string,
	boolean: string.xor_boolean,
	variant: string.xor_variant,
	constant: string.xor_variant,
	shadow: string.xor_variant}



boolean.add_table={
	empty: boolean.add_empty,
	null: boolean.with_null,
	integer: boolean.add_integer,
	double: boolean.add_double,
	date: boolean.add_date,
	string: boolean.add_string,
	boolean: boolean.add_boolean,
	variant: boolean.add_variant,
	constant: boolean.add_variant,
	shadow: boolean.add_variant}

boolean.sub_table={
	empty: boolean.sub_empty,
	null: boolean.with_null,
	integer: boolean.sub_integer,
	double: boolean.sub_double,
	date: boolean.sub_date,
	string: boolean.sub_string,
	boolean: boolean.sub_boolean,
	variant: boolean.sub_variant,
	constant: boolean.sub_variant,
	shadow: boolean.sub_variant}

boolean.mul_table={
	empty: boolean.mul_empty,
	null: boolean.with_null,
	integer: boolean.mul_integer,
	double: boolean.mul_double,
	date: boolean.mul_date,
	string: boolean.mul_string,
	boolean: boolean.mul_boolean,
	variant: boolean.mul_variant,
	constant: boolean.mul_variant,
	shadow: boolean.mul_variant}

boolean.div_table={
	empty: boolean.div_empty,
	null: boolean.with_null,
	integer: boolean.div_integer,
	double: boolean.div_double,
	date: boolean.div_date,
	string: boolean.div_string,
	boolean: boolean.div_boolean,
	variant: boolean.div_variant,
	constant: boolean.div_variant,
	shadow: boolean.div_variant}

boolean.floordiv_table={
	empty: boolean.floordiv_empty,
	null: boolean.with_null,
	integer: boolean.floordiv_integer,
	double: boolean.floordiv_double,
	date: boolean.floordiv_date,
	string: boolean.floordiv_string,
	boolean: boolean.floordiv_boolean,
	variant: boolean.floordiv_variant,
	constant: boolean.floordiv_variant,
	shadow: boolean.floordiv_variant}

boolean.mod_table={
	empty: boolean.mod_empty,
	null: boolean.with_null,
	integer: boolean.mod_integer,
	double: boolean.mod_double,
	date: boolean.mod_date,
	string: boolean.mod_string,
	boolean: boolean.mod_boolean,
	variant: boolean.mod_variant,
	constant: boolean.mod_variant,
	shadow: boolean.mod_variant}

boolean.pow_table={
	empty: boolean.pow_empty,
	null: boolean.with_null,
	integer: boolean.pow_integer,
	double: boolean.pow_double,
	date: boolean.pow_date,
	string: boolean.pow_string,
	boolean: boolean.pow_boolean,
	variant: boolean.pow_variant,
	constant: boolean.pow_variant,
	shadow: boolean.pow_variant}



boolean.eq_table={
	empty: boolean.eq_empty,
	null: boolean.with_null,
	integer: boolean.eq_integer,
	double: boolean.eq_double,
	date: boolean.eq_date,
	string: boolean.eq_string,
	boolean: boolean.eq_boolean,
	variant: boolean.eq_variant,
	constant: boolean.eq_variant,
	shadow: boolean.eq_variant}

boolean.ne_table={
	empty: boolean.ne_empty,
	null: boolean.with_null,
	integer: boolean.ne_integer,
	double: boolean.ne_double,
	date: boolean.ne_date,
	string: boolean.ne_string,
	boolean: boolean.ne_boolean,
	variant: boolean.ne_variant,
	constant: boolean.ne_variant,
	shadow: boolean.ne_variant}

boolean.lt_table={
	empty: boolean.lt_empty,
	null: boolean.with_null,
	integer: boolean.lt_integer,
	double: boolean.lt_double,
	date: boolean.lt_date,
	string: boolean.lt_string,
	boolean: boolean.lt_boolean,
	variant: boolean.lt_variant,
	constant: boolean.lt_variant,
	shadow: boolean.lt_variant}

boolean.gt_table={
	empty: boolean.gt_empty,
	null: boolean.with_null,
	integer: boolean.gt_integer,
	double: boolean.gt_double,
	date: boolean.gt_date,
	string: boolean.gt_string,
	boolean: boolean.gt_boolean,
	variant: boolean.gt_variant,
	constant: boolean.gt_variant,
	shadow: boolean.gt_variant}

boolean.le_table={
	empty: boolean.le_empty,
	null: boolean.with_null,
	integer: boolean.le_integer,
	double: boolean.le_double,
	date: boolean.le_date,
	string: boolean.le_string,
	boolean: boolean.le_boolean,
	variant: boolean.le_variant,
	constant: boolean.le_variant,
	shadow: boolean.le_variant}

boolean.ge_table={
	empty: boolean.ge_empty,
	null: boolean.with_null,
	integer: boolean.ge_integer,
	double: boolean.ge_double,
	date: boolean.ge_date,
	string: boolean.ge_string,
	boolean: boolean.ge_boolean,
	variant: boolean.ge_variant,
	constant: boolean.ge_variant,
	shadow: boolean.ge_variant}



boolean.and_table={
	empty: boolean.and_empty,
	null: boolean.and_null,
	integer: boolean.and_integer,
	double: boolean.and_double,
	date: boolean.and_date,
	string: boolean.and_string,
	boolean: boolean.and_boolean,
	variant: boolean.and_variant,
	constant: boolean.and_variant,
	shadow: boolean.and_variant}

boolean.or_table={
	empty: boolean.or_empty,
	null: boolean.or_null,
	integer: boolean.or_integer,
	double: boolean.or_double,
	date: boolean.or_date,
	string: boolean.or_string,
	boolean: boolean.or_boolean,
	variant: boolean.or_variant,
	constant: boolean.or_variant,
	shadow: boolean.or_variant}

boolean.xor_table={
	empty: boolean.xor_empty,
	null: boolean.xor_null,
	integer: boolean.xor_integer,
	double: boolean.xor_double,
	date: boolean.xor_date,
	string: boolean.xor_string,
	boolean: boolean.xor_boolean,
	variant: boolean.xor_variant,
	constant: boolean.xor_variant,
	shadow: boolean.xor_variant}



from exceptions import *
from library import *
