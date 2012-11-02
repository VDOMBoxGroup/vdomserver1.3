
import datetime, re
from .. import errors
from ..subtypes import v_null, array, integer, string, empty


def ireplace(s1, s2, s3, count=0):
	return re.sub(re.compile(re.escape(s2), re.I), s3, s1, count)


def v_len(value):
	return integer(len(value.as_simple))

def v_strcomp(string1, string2, compare=None):
	string1, string2=string1.as_string, string2.as_string
	compare=0 if compare is None else compare.as_integer
	if compare<0 or compare>1: raise errors.invalid_procedure_call(name=u"strcomp")
	if string1 is v_null or string2 is v_null: return v_null
	return integer(cmp(string1.lower(), string2.lower())) \
		if compare else integer(cmp(string1, string2))

def v_replace(expression, find, replacewith, start=None, count=None, compare=None):
	expression, find=expression.as_string, find.as_string
	replacewith=replacewith.as_string
	start=0 if start is None else start.as_integer-1
	if start<0: raise errors.invalid_procedure_call(name=u"replace")
	compare=0 if compare is None else compare.as_integer
	if compare<0 or compare>1: raise errors.invalid_procedure_call(name=u"replace")
	if count is None:
		return string(ireplace(expression[start:], find, replacewith)) \
			if compare else string(expression[start:].replace(find, replacewith))
	else:
		count=count.as_integer
		if count<0: raise errors.invalid_procedure_call(name=u"replace")
		return string(ireplace(expression[start:], find, replacewith, count)) \
			if compare else string(expression[start:].replace(find, replacewith, count))

def v_split(expression, delimiter=None, count=None, compare=None):
	delimiter=u" " if delimiter is None else delimiter.as_string
	count=-1 if count is None else count.as_integer
	if count<-1:
		raise errors.invalid_procedure_call(name=u"split")
	compare=0 if compare is None else compare.as_integer
	if compare<0 or compare>1: raise errors.invalid_procedure_call(name=u"split")
	if compare:
		strings=ireplace(as_string(expression), delimiter,
			delimiter.lower()).split(delimiter.lower())
	else:
		strings=expression.as_string.split(delimiter)
	if count>-1: strings=strings[:count+1]
	return array([string(string1) for string1 in strings])


def v_lcase(string1):
	return string(string1.as_string.lower())

def v_ucase(string1):
	return string(string1.as_string.upper())


def v_instr(argument1, argument2, argument3=None, compare=None):
	if argument3 is None:
		string1, string2, start=argument1.as_simple, argument2.as_simple, 0
	else:
		string1, string2, start=argument2.as_simple, argument3.as_simple, argument1.as_integer-1
		if start<0: raise errors.invalid_procedure_call(name=u"instr")
	compare=0 if compare is None else compare.as_integer
	if compare<0 or compare>1: raise errors.invalid_procedure_call(name=u"instr")
	if string1 is v_null or string2 is v_null: return v_null
	return integer(string1.as_string.lower().find(string2.as_string.lower(), start)+1) \
		if compare else integer(string1.as_string.find(string2.as_string, start)+1)

def v_instrrev(argument1, argument2, start=None, compare=None):
	if start is None:
		string1, string2, start=argument1.as_simple, argument2.as_simple, None
	else:
		string1, string2, start=argument1.as_simple, argument2.as_simple, start.as_integer
		if start==0: start=None
		elif start<1: raise errors.invalid_procedure_call(name=u"instrrev")
	compare=0 if compare is None else compare.as_integer
	if compare<0 or compare>1: raise errors.invalid_procedure_call(name=u"instrrev")
	if string1 is v_null or string2 is v_null: return v_null
	print ">>", compare, string1.as_string, string2.as_string, start, string1.as_string.rfind(string2.as_string, 0, start)
	return integer(string1.as_string.lower().rfind(string2.as_string.lower(), 0, start)+1) \
		if compare else integer(string1.as_string.rfind(string2.as_string, 0, start)+1)
	

def v_left(string1, length):
	length=length.as_integer
	if length<0: raise errors.invalid_procedure_call(name=u"left")
	return string(string1.as_string[0:length])

def v_right(string1, length):
	length=length.as_integer
	if length<0: raise errors.invalid_procedure_call(name=u"right")
	return string(string1.as_string[-length:])

def v_mid(string1, start, length=None):
	start=start.as_integer-1
	if start<0: raise errors.invalid_procedure_call(name=u"mid")
	if length is None:
		return string(string1.as_string[start:])
	else:
		length=length.as_integer
		if length<0: raise errors.invalid_procedure_call(name=u"mid")
		return string(string1.as_string[start:start+length])


def v_trim(string1):
	return string(string1.as_string.strip())

def v_ltrim(string1):
	return string(string1.as_string.lstrip())

def v_rtrim(string1):
	return string(string1.as_string.rstrip())


def v_space(number):
	number=number.as_integer
	if number<0: raise errors.invalid_procedure_call(name=u"space")
	return string(u" "*number)

def v_string(number, character):
	number, character=number.as_integer, character.as_simple
	if character is v_null: return v_null
	if isinstance(character, (integer, empty)):
		try: return string(unichr(character)*number)
		except ValueError: raise errors.invalid_procedure_call(name=u"string")
	elif isinstance(character, string):
		return string(unicode(character)[0]*number)
	else:
		raise errors.type_mismatch

def v_strreverse(string1):
	return string(string1.as_string[::-1])


def v_escape(string1):
	#return string(escape(as_string(string1)))
	return string(string1.as_string.encode("url"))

def v_unescape(string1):
	#return string(unescape(as_string(string1)))
	return string(string1.as_string.decode("url"))
