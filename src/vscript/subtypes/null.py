
from .. import errors, types


class null(object):

	def __init__(self):
		pass

	def __call__(self, *arguments, **keywords):
		raise errors.type_mismatch


	def get_type_code(self):
		return 1

	def get_type_name(self):
		return "Null"


	def with_null(self, another):
		return v_null


	def and_boolean(self, another):
		return v_null if another.value else boolean(v_false_value)

	def or_boolean(self, another):
		return boolean(v_true_value) if another.value else v_null

	def xor_boolean(self, another):
		return v_null


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
		return null.add_table.get(type(another), null.add_unknown)(self, another)

	def __sub__(self, another):
		return null.sub_table.get(type(another), null.sub_unknown)(self, another)

	def __mul__(self, another):
		return null.mul_table.get(type(another), null.mul_unknown)(self, another)

	def __div__(self, another):
		return null.div_table.get(type(another), null.div_unknown)(self, another)

	def __floordiv__(self, another):
		return null.floordiv_table.get(type(another), null.floordiv_unknown)(self, another)

	def __mod__(self, another):
		return null.mod_table.get(type(another), null.mod_unknown)(self, another)

	def __pow__(self, another):
		return null.pow_table.get(type(another), null.pow_unknown)(self, another)


	def __eq__(self, another):
		return null.eq_table.get(type(another), null.eq_unknown)(self, another)

	def __ne__(self, another):
		return null.ne_table.get(type(another), null.ne_unknown)(self, another)

	def __lt__(self, another):
		return null.lt_table.get(type(another), null.lt_unknown)(self, another)

	def __gt__(self, another):
		return null.gt_table.get(type(another), null.gt_unknown)(self, another)

	def __le__(self, another):
		return null.le_table.get(type(another), null.le_unknown)(self, another)

	def __ge__(self, another):
		return null.ge_table.get(type(another), null.ge_unknown)(self, another)

	__hash__ = object.__hash__


	def __and__(self, another):
		return null.and_table.get(type(another), null.and_unknown)(self, another)

	def __or__(self, another):
		return null.or_table.get(type(another), null.or_unknown)(self, another)

	def __xor__(self, another):
		return null.xor_table.get(type(another), null.xor_unknown)(self, another)


	def __invert__(self):
		return v_null
		
	def __neg__(self):
		return v_null

	def __pos__(self):
		return v_null

	def __abs__(self):
		return v_null


	def __copy__(self):
		return self

	def __deepcopy__(self, memo={}):
		return self


	def __int__(self):
		raise errors.type_mismatch

	def __str__(self):
		return "null"

	def __unicode__(self):
		return u"null"

	def __nonzero__(self):
		raise errors.type_mismatch


	def __repr__(self):
		return "NULL@%s"%object.__repr__(self)[-9:-1]


v_null=null()


from .boolean import boolean, v_true_value, v_false_value
