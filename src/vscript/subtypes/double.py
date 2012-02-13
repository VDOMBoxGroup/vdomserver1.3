
import sys
from math import floor, fabs
from .. import errors
from ..primitives import subtype


nan=float("nan")
infinity=float("inf")


class double(subtype):

	def __init__(self, value):
		self._value=value


	value=property(lambda self: self._value)


	code=property(lambda self: 5)
	name=property(lambda self: "Double")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: unicode(self))


	def __invert__(self):
		return integer(~int(round(self._value)))
		
	def __neg__(self):
		return double(-self._value)

	def __pos__(self):
		return double(+self._value)

	def __abs__(self):
		return double(fabs(self._value))


	def __int__(self):
		return int(round(self._value))

	def __float__(self):
		return self._value
	
	def __unicode__(self):
		if self._value==nan:
			return u"NaN"
		elif self._value==infinity:
			return u"Infinity"
		elif self._value==-infinity:
			return u"-Infinity"
		elif floor(self._value)==self._value:
			return unicode(int(self._value))
		else:
			return unicode(self._value)
	
	def __nonzero__(self):
		return bool(self._value)


	def __hash__(self):
		return hash(self._value)

	def __repr__(self):
		return "DOUBLE@%08X:%r"%(id(self), self._value)


from .boolean import boolean, true, false
from .date import date
from .empty import empty, v_empty
from .generic import generic
from .integer import integer
from .null import null, v_null
from .string import string


double.add_table={
	empty: lambda self, another: double(self._value+0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(self._value+int(another)),
	double: lambda self, another: double(self._value+float(another)),
	date: lambda self, another: date(self._value+float(another)).check,
	string: lambda self, another: double(self._value+float(another)),
	boolean: lambda self, another: double(self._value+int(another))}

double.sub_table={
	empty: lambda self, another: double(self._value-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(self._value-int(another)),
	double: lambda self, another: double(self._value-float(another)),
	date: lambda self, another: date(self._value-float(another)).check,
	string: lambda self, another: double(self._value-float(another)),
	boolean: lambda self, another: double(self._value-int(another))}

double.mul_table={
	empty: lambda self, another: double(self._value*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(self._value*int(another)),
	double: lambda self, another: double(self._value*float(another)),
	date: lambda self, another: double(self._value*float(another)),
	string: lambda self, another: double(self._value*float(another)),
	boolean: lambda self, another: double(self._value*int(another))}

double.div_table={
	empty: lambda self, another: double(self._value/0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(self._value/int(another)),
	double: lambda self, another: double(self._value/float(another)),
	date: lambda self, another: double(self._value/float(another)),
	string: lambda self, another: double(self._value/float(another)),
	boolean: lambda self, another: double(self._value/int(another))}

double.floordiv_table={
	empty: lambda self, another: integer(int(round(self._value))//0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(round(self._value))//int(another)),
	double: lambda self, another: integer(int(round(self._value))//int(round(float(another)))),
	date: lambda self, another: integer(int(round(self._value))//int(round(float(another)))),
	string: lambda self, another: integer(int(round(self._value))//int(round(float(another)))),
	boolean: lambda self, another: integer(int(round(self._value))//int(another))}

double.mod_table={
	empty: lambda self, another: integer(int(round(self._value))%0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(round(self._value))%int(another)),
	double: lambda self, another: integer(int(round(self._value))%int(round(float(another)))),
	date: lambda self, another: integer(int(round(self._value))%int(round(float(another)))),
	string: lambda self, another: integer(int(round(self._value))%int(round(float(another)))),
	boolean: lambda self, another: integer(int(round(self._value))%int(another))}

double.pow_table={
	empty: lambda self, another: double(self._value**0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(self._value**int(another)),
	double: lambda self, another: double(self._value**float(another)),
	date: lambda self, another: double(self._value**float(another)),
	string: lambda self, another: double(self._value**float(another)),
	boolean: lambda self, another: double(self._value**int(another))}


double.eq_table={
	empty: lambda self, another: boolean(true) if self._value==0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value==float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==int(another) else boolean(false)}

double.ne_table={
	empty: lambda self, another: boolean(true) if self._value!=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value!=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value!=int(another) else boolean(false)}

double.lt_table={
	empty: lambda self, another: boolean(true) if self._value<0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value<float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value<int(another) else boolean(false)}

double.gt_table={
	empty: lambda self, another: boolean(true) if self._value>0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value>float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value>int(another) else boolean(false)}

double.le_table={
	empty: lambda self, another: boolean(true) if self._value<=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value<=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value<=int(another) else boolean(false)}

double.ge_table={
	empty: lambda self, another: boolean(true) if self._value>=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if self._value>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if self._value>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if self._value>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value>=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value>=int(another) else boolean(false)}


double.and_table={
	empty: lambda self, another: integer(int(round(self._value))&0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(round(self._value))&int(another)),
	double: lambda self, another: integer(int(round(self._value))&int(round(float(another)))),
	date: lambda self, another: integer(int(round(self._value))&int(round(float(another)))),
	string: lambda self, another: integer(int(round(self._value))&int(round(float(another)))),
	boolean: lambda self, another: integer(int(round(self._value))&int(another))}

double.or_table={
	empty: lambda self, another: integer(int(round(self._value))|0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(round(self._value))|int(another)),
	double: lambda self, another: integer(int(round(self._value))|int(round(float(another)))),
	date: lambda self, another: integer(int(round(self._value))|int(round(float(another)))),
	string: lambda self, another: integer(int(round(self._value))|int(round(float(another)))),
	boolean: lambda self, another: integer(int(round(self._value))|int(another))}

double.xor_table={
	empty: lambda self, another: integer(int(round(self._value))^0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(round(self._value))^int(another)),
	double: lambda self, another: integer(int(round(self._value))^int(round(float(another)))),
	date: lambda self, another: integer(int(round(self._value))^int(round(float(another)))),
	string: lambda self, another: integer(int(round(self._value))^int(round(float(another)))),
	boolean: lambda self, another: integer(int(round(self._value))^int(another))}
