
import sys
from .. import errors, types


class string(object):

	def __init__(self, value):
		self.value=value

	def __call__(self, *arguments, **keywords):
		raise errors.type_mismatch


	def get_type_code(self):
		return 8

	def get_type_name(self):
		return "String"


	def add_empty(self, another):
		return double(float(self.value)+0)

	def sub_empty(self, another):
		return double(float(self.value)-0)

	def mul_empty(self, another):
		return double(float(self.value)*0)

	def div_empty(self, another):
		return double(float(self.value)/0)

	def floordiv_empty(self, another):
		return integer(int(round(float(self.value)))//0)

	def mod_empty(self, another):
		return integer(int(round(float(self.value)))%0)

	def pow_empty(self, another):
		return double(float(self.value)**0)


	def eq_empty(self, another):
		return boolean(v_true_value) if self.value==u"" else boolean(v_false_value)

	def ne_empty(self, another):
		return boolean(v_true_value) if self.value!=u"" else boolean(v_false_value)

	def lt_empty(self, another):
		return boolean(v_true_value) if self.value<u"" else boolean(v_false_value)

	def gt_empty(self, another):
		return boolean(v_true_value) if self.value>u"" else boolean(v_false_value)

	def le_empty(self, another):
		return boolean(v_true_value) if self.value<=u"" else boolean(v_false_value)

	def ge_empty(self, another):
		return boolean(v_true_value) if self.value>=u"" else boolean(v_false_value)


	def and_empty(self, another):
		return integer(int(self.value)&0)

	def or_empty(self, another):
		return integer(int(self.value)|0)

	def xor_empty(self, another):
		return integer(int(self.value)^0)


	def with_null(self, another):
		return v_null


	def and_null(self, another):
		return v_null

	def or_null(self, another):
		return v_null

	def xor_null(self, another):
		return v_null


	def add_integer(self, another):
		return double(float(self.value)+another.value)

	def sub_integer(self, another):
		return double(float(self.value)-another.value)

	def mul_integer(self, another):
		return double(float(self.value)*another.value)

	def div_integer(self, another):
		return double(float(self.value)/another.value)

	def floordiv_integer(self, another):
		return integer(int(round(float(self.value)))//another.value)

	def mod_integer(self, another):
		return integer(int(round(float(self.value)))%another.value)

	def pow_integer(self, another):
		return double(float(self.value)**another.value)


	def eq_integer(self, another):
		return boolean(v_true_value) if int(self.value)==another.value else boolean(v_false_value)

	def ne_integer(self, another):
		return boolean(v_true_value) if int(self.value)!=another.value else boolean(v_false_value)

	def lt_integer(self, another):
		return boolean(v_true_value) if int(self.value)<another.value else boolean(v_false_value)

	def gt_integer(self, another):
		return boolean(v_true_value) if int(self.value)>another.value else boolean(v_false_value)

	def le_integer(self, another):
		return boolean(v_true_value) if int(self.value)<=another.value else boolean(v_false_value)

	def ge_integer(self, another):
		return boolean(v_true_value) if int(self.value)>=another.value else boolean(v_false_value)


	def and_integer(self, another):
		return integer(int(self.value)&another.value)

	def or_integer(self, another):
		return integer(int(self.value)|another.value)

	def xor_integer(self, another):
		return integer(int(self.value)^another.value)


	def add_double(self, another):
		return double(float(self.value)+another.value)

	def sub_double(self, another):
		return double(float(self.value)-another.value)

	def mul_double(self, another):
		return double(float(self.value)*another.value)

	def div_double(self, another):
		return double(float(self.value)/another.value)

	def floordiv_double(self, another):
		return integer(int(round(float(self.value)))//another.value)

	def mod_double(self, another):
		return integer(int(round(float(self.value)))%another.value)

	def pow_double(self, another):
		return double(float(self.value)**another.value)


	def eq_double(self, another):
		return boolean(v_true_value) if float(self.value)==another.value else boolean(v_false_value)

	def ne_double(self, another):
		return boolean(v_true_value) if float(self.value)!=another.value else boolean(v_false_value)

	def lt_double(self, another):
		return boolean(v_true_value) if float(self.value)<another.value else boolean(v_false_value)

	def gt_double(self, another):
		return boolean(v_true_value) if float(self.value)>another.value else boolean(v_false_value)

	def le_double(self, another):
		return boolean(v_true_value) if float(self.value)<=another.value else boolean(v_false_value)

	def ge_double(self, another):
		return boolean(v_true_value) if float(self.value)>=another.value else boolean(v_false_value)


	def and_double(self, another):
		return integer(int(self.value)&int(round(another.value)))

	def or_double(self, another):
		return integer(int(self.value)|int(round(another.value)))

	def xor_double(self, another):
		return integer(int(self.value)^int(round(another.value)))


	def add_date(self, another):
		return date(float(self.value)+another.value).check()

	def sub_date(self, another):
		return date(float(self.value)-another.value).check()

	def mul_date(self, another):
		return double(float(self.value)*another.value)

	def div_date(self, another):
		return double(float(self.value)/another.value)

	def floordiv_date(self, another):
		return integer(int(round(float(self.value)))//int(round(another.value)))

	def mod_date(self, another):
		return integer(int(round(float(self.value)))%int(round(another.value)))

	def pow_date(self, another):
		return double(float(self.value)**another.value)


	def eq_date(self, another):
		return boolean(v_true_value) if float(self.value)==another.value else boolean(v_false_value)

	def ne_date(self, another):
		return boolean(v_true_value) if float(self.value)!=another.value else boolean(v_false_value)

	def lt_date(self, another):
		return boolean(v_true_value) if float(self.value)<another.value else boolean(v_false_value)

	def gt_date(self, another):
		return boolean(v_true_value) if float(self.value)>another.value else boolean(v_false_value)

	def le_date(self, another):
		return boolean(v_true_value) if float(self.value)<=another.value else boolean(v_false_value)

	def ge_date(self, another):
		return boolean(v_true_value) if float(self.value)>=another.value else boolean(v_false_value)


	def and_date(self, another):
		return integer(int(round(float(self.value)))&int(round(another.value)))

	def or_date(self, another):
		return integer(int(round(float(self.value)))|int(round(another.value)))

	def xor_date(self, another):
		return integer(int(round(float(self.value)))^int(round(another.value)))


	def add_string(self, another):
		return string(self.value+another.value)

	def sub_string(self, another):
		return double(float(self.value)-float(another.value))

	def mul_string(self, another):
		return double(float(self.value)*float(another.value))

	def div_string(self, another):
		return double(float(self.value)/float(another.value))

	def floordiv_string(self, another):
		return integer(int(round(float(self.value)))//int(round(float(another.value))))

	def mod_string(self, another):
		return integer(int(round(float(self.value)))%int(round(float(another.value))))

	def pow_string(self, another):
		return double(float(self.value)**float(another.value))


	def eq_string(self, another):
		return boolean(v_true_value) if self.value==another.value else boolean(v_false_value)

	def ne_string(self, another):
		return boolean(v_true_value) if self.value!=another.value else boolean(v_false_value)

	def lt_string(self, another):
		return boolean(v_true_value) if self.value<another.value else boolean(v_false_value)

	def gt_string(self, another):
		return boolean(v_true_value) if self.value>another.value else boolean(v_false_value)

	def le_string(self, another):
		return boolean(v_true_value) if self.value<=another.value else boolean(v_false_value)

	def ge_string(self, another):
		return boolean(v_true_value) if self.value>=another.value else boolean(v_false_value)


	def and_string(self, another):
		return integer(int(self.value)&int(another.value))

	def or_string(self, another):
		return integer(int(self.value)|int(another.value))

	def xor_string(self, another):
		return integer(int(self.value)^int(another.value))


	def add_boolean(self, another):
		return double(float(self.value)+another.value)

	def sub_boolean(self, another):
		return double(float(self.value)-another.value)

	def mul_boolean(self, another):
		return double(float(self.value)*another.value)

	def div_boolean(self, another):
		return double(float(self.value)/another.value)

	def floordiv_boolean(self, another):
		return integer(int(round(float(self.value)))//another.value)

	def mod_boolean(self, another):
		return integer(int(round(float(self.value)))%another.value)

	def pow_boolean(self, another):
		return double(float(self.value)**another.value)


	def eq_boolean(self, another):
		keyword=u"True" if another.value==v_true_value else u"False"
		return boolean(v_true_value) if self.value==keyword else boolean(v_false_value)

	def ne_boolean(self, another):
		keyword=u"True" if another.value==v_true_value else u"False"
		return boolean(v_true_value) if self.value!=keyword else boolean(v_false_value)

	def lt_boolean(self, another):
		keyword=u"True" if another.value==v_true_value else u"False"
		return boolean(v_true_value) if self.value<keyword else boolean(v_false_value)

	def gt_boolean(self, another):
		keyword=u"True" if another.value==v_true_value else u"False"
		return boolean(v_true_value) if self.value>keyword else boolean(v_false_value)

	def le_boolean(self, another):
		keyword=u"True" if another.value==v_true_value else u"False"
		return boolean(v_true_value) if self.value<=keyword else boolean(v_false_value)

	def ge_boolean(self, another):
		keyword=u"True" if another.value==v_true_value else u"False"
		return boolean(v_true_value) if self.value>=keyword else boolean(v_false_value)


	def and_boolean(self, another):
		return integer(int(self.value)&another.value)

	def or_boolean(self, another):
		return integer(int(self.value)|another.value)

	def xor_boolean(self, another):
		return integer(int(self.value)^another.value)


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
			return string.add_table.get(type(another), string.add_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __sub__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return string.sub_table.get(type(another), string.sub_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __mul__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return string.mul_table.get(type(another), string.mul_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __div__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return string.div_table.get(type(another), string.div_unknown)(self, another)
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
			return string.floordiv_table.get(type(another), string.floordiv_unknown)(self, another)
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
			return string.mod_table.get(type(another), string.mod_unknown)(self, another)
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
			return string.pow_table.get(type(another), string.pow_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback


	def __eq__(self, another):
		return string.eq_table.get(type(another), string.eq_unknown)(self, another)

	def __ne__(self, another):
		return string.ne_table.get(type(another), string.ne_unknown)(self, another)

	def __lt__(self, another):
		return string.lt_table.get(type(another), string.lt_unknown)(self, another)

	def __gt__(self, another):
		return string.gt_table.get(type(another), string.gt_unknown)(self, another)

	def __le__(self, another):
		return string.le_table.get(type(another), string.le_unknown)(self, another)

	def __ge__(self, another):
		return string.ge_table.get(type(another), string.ge_unknown)(self, another)

	def __hash__(self):
		return hash(self.value)


	def __and__(self, another):
		return string.and_table.get(type(another), string.and_unknown)(self, another)

	def __or__(self, another):
		return string.or_table.get(type(another), string.or_unknown)(self, another)

	def __xor__(self, another):
		return string.xor_table.get(type(another), string.xor_unknown)(self, another)


	def __invert__(self):
		return integer(~int(round(float(self.value))))
		
	def __neg__(self):
		return integer(-int(self.value))

	def __pos__(self):
		return integer(+int(self.value))

	def __abs__(self):
		return integer(abs(int(self.value)))


	def __int__(self):
		return int(self.value)

	def __float__(self):
		return float(self.value)

	def __str__(self):
		return str(self.value)

	def __unicode__(self):
		return unicode(self.value)

	def __nonzero__(self):
		return bool(self.value)


	def __repr__(self):
		return "STRING@%s:%s"%(object.__repr__(self)[-9:-1], repr(self.value))


from .null import null, v_null
from .integer import integer
from .double import double, nan, infinity
from .date import date
from .boolean import boolean, v_true_value, v_false_value
from .generic import generic
