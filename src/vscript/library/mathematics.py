
from random import random, seed
from .. import errors
from ..subtypes import integer, double


last_random=random()


def v_abs(number):
	return abs(number)
	#number=number.as_simple
	#if isinstance(number, (integer, boolean, empty)):
	#	return integer(abs(number.as_integer))
	#elif isinstance(number, (double, string, date)):
	#	return double(abs(number.as_double))
	#else: raise errors.type_mismatch

def v_sgn(number):
	number=number.as_integer
	return integer(-1 if number<0 else 1 if number>0 else 0)

def v_round(number, digits=None):
	return double(round(number.as_double)) if digits is None \
		else double(round(number.as_double, digits.as_integer))


def v_exp(number):
	number=number.as_double
	# 709.782712893 - highest value from MSDN
	if number>709.782712893: raise errors.invalid_procedure_call(name=u"exp")
	return double(math.exp(number))

def v_int(number):
	return integer(math.floor(number.as_double))
	
def v_fix(number):
	return integer(math.ceil(number.as_double))

def v_log(number):
	number=number.as_double
	if number<=0: raise errors.invalid_procedure_call(name=u"log")
	return double(math.log(number))

def v_sqr(number):
	number=number.as_double
	if number<0: raise errors.invalid_procedure_call(name=u"sqr")
	return double(math.sqrt(number))


def v_atn(number):
	return double(math.atan(number.as_double))

def v_cos(number):
	return double(math.cos(number.as_double))

def v_sin(number):
	return double(math.sin(number.as_double))

def v_tan(number):
	return double(math.tan(number.as_double))


def v_rnd(number=None):
	global last_random
	number=1 if number is None else number.as_double
	if number<0:
		seed(number)
		value=random()
		last_random=value
	elif number>0:
		value=random()
		last_random=value
	else:
		value=last_random
	return double(value)
