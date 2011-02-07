
import sys

import errors, types



class empty(object):

	def __init__(self):
		pass

	def __call__(self, *arguments, **keywords):
		raise errors.type_mismatch



	def get_type_code(self):
		return 0

	def get_type_name(self):
		return "Empty"

    

	def add_empty(self, another):
		return integer(0+0)

	def sub_empty(self, another):
		return integer(0-0)

	def mul_empty(self, another):
		return integer(0*0)

	def div_empty(self, another):
		return double(0.0/0)

	def floordiv_empty(self, another):
		return integer(0//0)

	def mod_empty(self, another):
		return integer(0%0)

	def pow_empty(self, another):
		return double(0.0**0)



	def eq_empty(self, another):
		return boolean(v_true_value)

	def ne_empty(self, another):
		return boolean(v_false_value)

	def lt_empty(self, another):
		return boolean(v_false_value)

	def gt_empty(self, another):
		return boolean(v_false_value)

	def le_empty(self, another):
		return boolean(v_true_value)

	def ge_empty(self, another):
		return boolean(v_true_value)
		


	def and_empty(self, another):
		return integer(0&0)

	def or_empty(self, another):
		return integer(0|0)

	def xor_empty(self, another):
		return integer(0^0)


	
	def with_null(self, another):
		return v_null
		


	def and_null(self, another):
		return v_null

	def or_null(self, another):
		return v_null

	def xor_null(self, another):
		return v_null


	
	def add_integer(self, another):
		return integer(0+another.value)

	def sub_integer(self, another):
		return integer(0-another.value)

	def mul_integer(self, another):
		return integer(0*another.value)

	def div_integer(self, another):
		return double(0.0/another.value)

	def floordiv_integer(self, another):
		return integer(0//another.value)

	def mod_integer(self, another):
		return integer(0%another.value)

	def pow_integer(self, another):
		return double(0.0**another.value)


	
	def eq_integer(self, another):
		return boolean(v_true_value) if 0==another.value else boolean(v_false_value)

	def ne_integer(self, another):
		return boolean(v_true_value) if 0!=another.value else boolean(v_false_value)

	def lt_integer(self, another):
		return boolean(v_true_value) if 0<another.value else boolean(v_false_value)

	def gt_integer(self, another):
		return boolean(v_true_value) if 0>another.value else boolean(v_false_value)

	def le_integer(self, another):
		return boolean(v_true_value) if 0<=another.value else boolean(v_false_value)

	def ge_integer(self, another):
		return boolean(v_true_value) if 0>=another.value else boolean(v_false_value)

	
	
	def and_integer(self, another):
		return integer(0&another.value)

	def or_integer(self, another):
		return integer(0|another.value)

	def xor_integer(self, another):
		return integer(0^another.value)


	
	def add_double(self, another):
		return double(0+another.value)

	def sub_double(self, another):
		return double(0-another.value)

	def mul_double(self, another):
		return double(0*another.value)

	def div_double(self, another):
		return double(0/another.value)

	def floordiv_double(self, another):
		return integer(0//int(round(another.value)))

	def mod_double(self, another):
		return integer(0%int(round(another.value)))

	def pow_double(self, another):
		return double(0**another.value)


	
	def eq_double(self, another):
		return boolean(v_true_value) if 0==another.value else boolean(v_false_value)

	def ne_double(self, another):
		return boolean(v_true_value) if 0!=another.value else boolean(v_false_value)

	def lt_double(self, another):
		return boolean(v_true_value) if 0<another.value else boolean(v_false_value)

	def gt_double(self, another):
		return boolean(v_true_value) if 0>another.value else boolean(v_false_value)

	def le_double(self, another):
		return boolean(v_true_value) if 0<=another.value else boolean(v_false_value)

	def ge_double(self, another):
		return boolean(v_true_value) if 0>=another.value else boolean(v_false_value)

	
	
	def and_double(self, another):
		return integer(0&int(round(another.value)))

	def or_double(self, another):
		return integer(0|int(round(another.value)))

	def xor_double(self, another):
		return integer(0^int(round(another.value)))


	
	def add_date(self, another):
		return date(0+another.value).check()

	def sub_date(self, another):
		return date(0-another.value).check()

	def mul_date(self, another):
		return double(0*another.value)

	def div_date(self, another):
		return double(0/another.value)

	def floordiv_date(self, another):
		return integer(0//int(round(another.value)))

	def mod_date(self, another):
		return integer(0%int(round(another.value)))

	def pow_date(self, another):
		return double(0**another.value)


	
	def eq_date(self, another):
		return boolean(v_true_value) if 0==another.value else boolean(v_false_value)

	def ne_date(self, another):
		return boolean(v_true_value) if 0!=another.value else boolean(v_false_value)

	def lt_date(self, another):
		return boolean(v_true_value) if 0<another.value else boolean(v_false_value)

	def gt_date(self, another):
		return boolean(v_true_value) if 0>another.value else boolean(v_false_value)

	def le_date(self, another):
		return boolean(v_true_value) if 0<=another.value else boolean(v_false_value)

	def ge_date(self, another):
		return boolean(v_true_value) if 0>=another.value else boolean(v_false_value)

	
	
	def and_date(self, another):
		return integer(0&int(round(another.value)))

	def or_date(self, another):
		return integer(0|int(round(another.value)))

	def xor_date(self, another):
		return integer(0^int(round(another.value)))



	def add_string(self, another):
		return string(""+another.value)

	def sub_string(self, another):
		return double(0-float(another.value))

	def mul_string(self, another):
		return double(0*float(another.value))

	def div_string(self, another):
		return double(0/float(another.value))

	def floordiv_string(self, another):
		return integer(0//int(round(float(another.value))))

	def mod_string(self, another):
		return integer(0%int(round(float(another.value))))

	def pow_string(self, another):
		return double(0**float(another.value))


	
	def eq_string(self, another):
		return boolean(v_true_value) if u""==another.value else boolean(v_false_value)

	def ne_string(self, another):
		return boolean(v_true_value) if u""!=another.value else boolean(v_false_value)

	def lt_string(self, another):
		return boolean(v_true_value) if u""<another.value else boolean(v_false_value)

	def gt_string(self, another):
		return boolean(v_true_value) if u"">another.value else boolean(v_false_value)

	def le_string(self, another):
		return boolean(v_true_value) if u""<=another.value else boolean(v_false_value)

	def ge_string(self, another):
		return boolean(v_true_value) if u"">=another.value else boolean(v_false_value)

		

	def and_string(self, another):
		return integer(0&int(another.value))

	def or_string(self, another):
		return integer(0|int(another.value))

	def xor_string(self, another):
		return integer(0^int(another.value))


	
	def add_boolean(self, another):
		return integer(0+another.value)

	def sub_boolean(self, another):
		return integer(0-another.value)

	def mul_boolean(self, another):
		return integer(0*another.value)

	def div_boolean(self, another):
		return double(0.0/another.value)

	def floordiv_boolean(self, another):
		return integer(0//another.value)

	def mod_boolean(self, another):
		return integer(0%another.value)

	def pow_boolean(self, another):
		return double(0.0**another.value)


	
	def eq_boolean(self, another):
		return boolean(v_true_value) if 0==another.value else boolean(v_false_value)

	def ne_boolean(self, another):
		return boolean(v_true_value) if 0!=another.value else boolean(v_false_value)

	def lt_boolean(self, another):
		return boolean(v_true_value) if 0<another.value else boolean(v_false_value)

	def gt_boolean(self, another):
		return boolean(v_true_value) if 0>another.value else boolean(v_false_value)

	def le_boolean(self, another):
		return boolean(v_true_value) if 0<=another.value else boolean(v_false_value)

	def ge_boolean(self, another):
		return boolean(v_true_value) if 0>=another.value else boolean(v_false_value)

	
	
	def and_boolean(self, another):
		return integer(0&another.value)

	def or_boolean(self, another):
		return integer(0|another.value)

	def xor_boolean(self, another):
		return integer(0^another.value)


	
	def add_variant(self, another):
		return self.__add__(another.value)

	def sub_variant(self, another):
		return self.__sub__(another.value)

	def mul_variant(self, another):
		return self.__mul__(another.value)

	def div_variant(self, another):
		return self.__div__(another.value)

	def floordiv_variant(self, another):
		return self.__floordiv__(another.value)

	def mod_variant(self, another):
		return self.__mod__(another.value)

	def pow_variant(self, another):
		return self.__pow__(another.value)



	def eq_variant(self, another):
		return self.__eq__(another.value)

	def ne_variant(self, another):
		return self.__ne__(another.value)

	def lt_variant(self, another):
		return self.__lt__(another.value)

	def gt_variant(self, another):
		return self.__gt__(another.value)

	def le_variant(self, another):
		return self.__le__(another.value)

	def ge_variant(self, another):
		return self.__ge__(another.value)


	
	def and_variant(self, another):
		return self.__and__(another.value)

	def or_variant(self, another):
		return self.__or__(another.value)

	def xor_variant(self, another):
		return self.__xor__(another.value)



	def add_unknown(self, another):
		raise errors.type_mismatch

	def sub_unknown(self, another):
		raise errors.type_mismatch

	def mul_unknown(self, another):
		raise errors.type_mismatch

	def div_unknown(self, another):
		raise errors.type_mismatch

	def floordiv_unknown(self, another):
		raise errors.type_mismatch

	def mod_unknown(self, another):
		raise errors.type_mismatch

	def pow_unknown(self, another):
		raise errors.type_mismatch
	

	
	def eq_unknown(self, another):
		raise errors.type_mismatch

	def ne_unknown(self, another):
		raise errors.type_mismatch

	def lt_unknown(self, another):
		raise errors.type_mismatch

	def gt_unknown(self, another):
		raise errors.type_mismatch

	def le_unknown(self, another):
		raise errors.type_mismatch

	def ge_unknown(self, another):
		raise errors.type_mismatch



	def and_unknown(self, another):
		raise errors.type_mismatch

	def or_unknown(self, another):
		raise errors.type_mismatch

	def xor_unknown(self, another):
		raise errors.type_mismatch



	def type_mismatch(self, another):
		raise errors.type_mismatch



	add_table=None
	sub_table=None
	mul_table=None
	div_table=None
	floordiv_table=None
	mod_table=None
	pow_table=None

	eq_table=None
	ne_table=None
	lt_table=None
	gt_table=None
	le_table=None
	ge_table=None

	and_table=None
	or_table=None
	xor_table=None


	
	def __add__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return empty.add_table.get(type(another), empty.add_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __sub__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return empty.sub_table.get(type(another), empty.sub_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __mul__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return empty.mul_table.get(type(another), empty.mul_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __div__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return empty.div_table.get(type(another), empty.div_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback
		except ZeroDivisionError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.division_by_zero, None, extraceback

	def __floordiv__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return empty.floordiv_table.get(type(another), empty.floordiv_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback
		except ZeroDivisionError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.division_by_zero, None, extraceback

	def __mod__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return empty.mod_table.get(type(another), empty.mod_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback
		except ZeroDivisionError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.division_by_zero, None, extraceback

	def __pow__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return empty.pow_table.get(type(another), empty.pow_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback
	

	
	def __eq__(self, another):
		return empty.eq_table.get(type(another), empty.eq_unknown)(self, another)

	def __ne__(self, another):
		return empty.ne_table.get(type(another), empty.ne_unknown)(self, another)

	def __lt__(self, another):
		return empty.lt_table.get(type(another), empty.lt_unknown)(self, another)

	def __gt__(self, another):
		return empty.gt_table.get(type(another), empty.gt_unknown)(self, another)

	def __le__(self, another):
		return empty.le_table.get(type(another), empty.le_unknown)(self, another)

	def __ge__(self, another):
		return empty.ge_table.get(type(another), empty.ge_unknown)(self, another)

	def __hash__(self):
		raise NotImplementedError


	def __and__(self, another):
		return empty.and_table.get(type(another), empty.and_unknown)(self, another)

	def __or__(self, another):
		return empty.or_table.get(type(another), empty.or_unknown)(self, another)

	def __xor__(self, another):
		return empty.xor_table.get(type(another), empty.xor_unknown)(self, another)



	def __invert__(self):
		return boolean(v_true_value)
		
	def __neg__(self):
		return integer(0)

	def __pos__(self):
		return integer(0)

	def __abs__(self):
		return integer(0)



	def __copy__(self):
		return self

	def __deepcopy__(self, memo={}):
		return self

	
	
	def __int__(self):
		return 0

	def __float__(self):
		return 0.0

	def __str__(self):
		return ""

	def __unicode__(self):
		return u""

	def __nonzero__(self):
		return False



	def __repr__(self):
		return "EMPTY@%s"%object.__repr__(self)[-9:-1]



v_empty=empty()



from null import null, v_null
from integer import integer
from double import double, nan, infinity
from date import date
from boolean import boolean, v_true_value, v_false_value
from generic import generic
