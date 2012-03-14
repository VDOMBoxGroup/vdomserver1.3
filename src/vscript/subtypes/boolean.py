
import sys
from .. import errors
from ..primitives import subtype


true=-1
false=0

v_true_value=true
v_false_value=false


class boolean(subtype):
	
	def __init__(self, value):
		self._value=true if value else false


	value=property(lambda self: self._value)


	code=property(lambda self: 11)
	name=property(lambda self: "Boolean")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_date=property(lambda self: float(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: unicode(self))
	

	def is_boolean(self, value):
		return self._value==value


	def __invert__(self):
		return boolean(~self._value)
		
	def __neg__(self):
		return integer(-self._value)

	def __pos__(self):
		return integer(+self._value)

	def __abs__(self):
		return integer(abs(self._value))


	def __int__(self):
		return self._value

	def __float__(self):
		return float(self._value)

	def __unicode__(self):
		return unicode(self._value)

	def __nonzero__(self):
		return self._value


	def __hash__(self):
		return hash(self._value)

	def __repr__(self):
		return "BOOLEAN@%08X:%s"%(id(self), "TRUE" if self._value==true else "FALSE")
	


from .date import date
from .double import double, nan, infinity
from .empty import empty, v_empty
from .generic import generic
from .integer import integer
from .null import null, v_null
from .string import string


boolean.add_table={
	empty: lambda self, another: integer(self._value+0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(self._value+int(another)),
	double: lambda self, another: double(self._value+float(another)),
	date: lambda self, another: date(self._value+float(another)),
	string: lambda self, another: double(self._value+float(another)),
	boolean: lambda self, another: integer(self._value+int(another))}

boolean.sub_table={
	empty: lambda self, another: integer(self._value-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(self._value-int(another)),
	double: lambda self, another: double(self._value+float(another)),
	date: lambda self, another: date(self._value-float(another)),
	string: lambda self, another: double(self._value-float(another)),
	boolean: lambda self, another: integer(self._value-int(another))}

boolean.mul_table={
	empty: lambda self, another: integer(self._value*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(self._value*int(another)),
	double: lambda self, another: double(self._value*float(another)),
	date: lambda self, another: double(self._value*float(another)),
	string: lambda self, another: double(self._value*float(another)),
	boolean: lambda self, another: integer(self._value*int(another))}

boolean.div_table={
	empty: lambda self, another: double(float(self._value)/0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(self._value/float(another)),
	double: lambda self, another: double(self._value/float(another)),
	date: lambda self, another: double(self._value/float(another)),
	string: lambda self, another: double(self._value/float(another)),
	boolean: lambda self, another: double(float(self._value)/int(another))}

boolean.floordiv_table={
	empty: lambda self, another: integer(self._value//0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(self._value//int(another)),
	double: lambda self, another: integer(self._value//int(round(float(another)))),
	date: lambda self, another: integer(self._value//int(round(float(another)))),
	string: lambda self, another: integer(self._value//int(round(float(another)))),
	boolean: lambda self, another: integer(self._value//int(another))}

boolean.mod_table={
	empty: lambda self, another: integer(self._value%0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(self._value%int(another)),
	double: lambda self, another: integer(self._value%int(round(float(another)))),
	date: lambda self, another: integer(self._value%int(round(float(another)))),
	string: lambda self, another: integer(self._value%int(round(float(another)))),
	boolean: lambda self, another: integer(self._value%int(another))}

boolean.pow_table={
	empty: lambda self, another: double(float(self._value)**0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(self._value**float(another)),
	double: lambda self, another: double(self._value**float(another)),
	date: lambda self, another: double(self._value**float(another)),
	string: lambda self, another: double(self._value**float(another)),
	boolean: lambda self, another: double(float(self._value)**int(another))}


boolean.eq_table={
	empty: lambda self, another: boolean(true) if another._value==0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if (u"True" if self._value==true else u"False")==unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==int(another) else boolean(false)}

boolean.ne_table={
	empty: lambda self, another: boolean(true) if another._value!=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if (u"True" if self._value!=true else u"False")==unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value!=int(another) else boolean(false)}

boolean.lt_table={
	empty: lambda self, another: boolean(true) if another._value<0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if (u"True" if self._value<true else u"False")==unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value<int(another) else boolean(false)}

boolean.gt_table={
	empty: lambda self, another: boolean(true) if another._value>0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if (u"True" if self._value>true else u"False")==unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value>int(another) else boolean(false)}

boolean.le_table={
	empty: lambda self, another: boolean(true) if another._value<=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if (u"True" if self._value<=true else u"False")==unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value<=int(another) else boolean(false)}

boolean.ge_table={
	empty: lambda self, another: boolean(true) if another._value>=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if (u"True" if self._value>=true else u"False")==unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value>=int(another) else boolean(false)}


boolean.and_table={
	empty: lambda self, another: integer(self._value&0),
	null: lambda self, another: v_null if self._value else boolean(false),
	integer: lambda self, another: integer(self._value&int(another)),
	double: lambda self, another: integer(self._value&int(round(float(another)))),
	date: lambda self, another: integer(self._value&int(round(float(another)))),
	string: lambda self, another: integer(self._value&int(another)),
	boolean: lambda self, another: boolean(self._value&int(another))}

boolean.or_table={
	empty: lambda self, another: integer(self._value|0),
	null: lambda self, another: boolean(true) if self._value else v_null,
	integer: lambda self, another: integer(self._value|int(another)),
	double: lambda self, another: integer(self._value|int(round(float(another)))),
	date: lambda self, another: integer(self._value|int(round(float(another)))),
	string: lambda self, another: integer(self._value|int(another)),
	boolean: lambda self, another: boolean(self._value|int(another))}

boolean.xor_table={
	empty: lambda self, another: integer(self._value^0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(self._value^int(another)),
	double: lambda self, another: integer(self._value^int(round(float(another)))),
	date: lambda self, another: integer(self._value^int(round(float(another)))),
	string: lambda self, another: integer(self._value^int(another)),
	boolean: lambda self, another: boolean(self._value^int(another))}
