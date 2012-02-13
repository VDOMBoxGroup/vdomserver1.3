
from .. import errors
from ..subtypes import array, boolean, date, double, empty, \
	generic, integer, nothing, null, string


def v_isarray(value):
	return v_true_value if isinstance(value.subtype, array) else v_false_value
	
def v_isdate(value):
	return v_true_value if isinstance(value.subtype, date) else v_false_value

def v_isempty(value):
	return v_true_value if isinstance(value.subtype, empty) else v_false_value
	
def v_isnothing(value):
	return v_true_value if isinstance(value.subtype, nothing) else v_false_value
	
def v_isnull(value):
	return v_true_value if isinstance(value.subtype, null) else v_false_value

	
def v_isnumeric(value):
	return v_true_value if isinstance(value.subtype, (integer, double)) else v_false_value
	
def v_isobject(value):
	return v_true_value if isinstance(value.subtype, generic) else v_false_value


def v_cbool(expression):
	return boolean(bool(expression.as_simple))

def v_cdate(expression):
	return date(expression.value)

def v_csng(expression):
	return double(float(expression.as_simple))

def v_cdbl(expression):
	return double(float(expression.as_simple))

def v_cbyte(expression):
	value=int(expression.as_simple)
	if value<0 or value>255: raise errors.invalid_procedure_call(name=u"cbyte")
	return integer(value)

def v_cint(expression):
	return integer(int(expression.as_simple))

def v_clng(expression):
	return integer(int(expression.as_simple))

def v_cstr(expression):
	return string(unicode(expression.as_simple))


def v_hex(number):
	number=number.as_integer
	string1=hex(number)[2:] if number>0 else \
		hex(0x100000000+number)[2:-1] if number<-0xFFFF else \
		hex(0x10000+number)[2:] if number<0 else "0"
	return string(unicode(string1.upper()))

def v_oct(number):
	number=number.as_integer
	string1=oct(number)[1:] if number>0 else \
		oct(0x100000000+number)[1:-1] if number<-0xFFFF else \
		oct(0x10000+number)[1:] if number<0 else "0"
	return string(unicode(string1))

def v_chr(number):
	return string(unichr(number.as_integer))

def v_asc(string1):
	string1=string1.as_string
	if len(string1)<1: raise errors.invalid_procedure_call(name=u"asc")
	return integer(ord(string1[0]))

def v_rgb(red, green, blue):
	red, green, blue=red.as_integer, green.as_integer, blue.as_integer
	return integer(blue+green*256+red*65535)
