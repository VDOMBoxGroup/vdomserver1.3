
import sys
from .. import errors
from ..primitives import subtype


class string(subtype):

	def __init__(self, value):
		self._value=value


	value=property(lambda self: self._value)


	code=property(lambda self: 8)
	name=property(lambda self: "String")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_date=property(lambda self: float(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: unicode(self))


	def is_string(self, value):
		return self._value==value


	def __iter__(self):
		for character in self._value: return variant(string(character))

	def __len__(self):
		return len(self._value)


	def __invert__(self):
		return integer(~int(round(float(self._value))))
		
	def __neg__(self):
		return integer(-int(self._value))

	def __pos__(self):
		return integer(+int(self._value))

	def __abs__(self):
		return integer(abs(int(self._value)))


	def __int__(self):
		try: return int(self._value)
		except ValueError: raise errors.type_mismatch

	def __float__(self):
		try: return float(self._value)
		except ValueError: raise errors.type_mismatch

	def __unicode__(self):
		return unicode(self._value)

	def __nonzero__(self):
		try: return bool(self._value)
		except ValueError: raise errors.type_mismatch


	def __hash__(self):
		return hash(self._value)

	def __repr__(self):
		return "STRING@%08X:%r"%(id(self), self._value)


from .boolean import boolean, true, false
from .date import date
from .double import double, nan, infinity
from .empty import empty, v_empty
from .generic import generic
from .integer import integer
from .null import null, v_null


string.add_table={
	empty: lambda self, another: double(float(self._value)+0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self._value)+int(another)),
	double: lambda self, another: double(float(self._value)+float(another)),
	date: lambda self, another: date(float(self._value)+float(another)),
	string: lambda self, another: string(self._value+unicode(another)),
	boolean: lambda self, another: double(float(self._value)+int(another))}

string.sub_table={
	empty: lambda self, another: double(float(self._value)-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self._value)-int(another)),
	double: lambda self, another: double(float(self._value)-float(another)),
	date: lambda self, another: date(float(self._value)-float(another)),
	string: lambda self, another: double(float(self._value)-float(another)),
	boolean: lambda self, another: double(float(self._value)-int(another))}

string.mul_table={
	empty: lambda self, another: double(float(self._value)*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self._value)*int(another)),
	double: lambda self, another: double(float(self._value)*float(another)),
	date: lambda self, another: double(float(self._value)*float(another)),
	string: lambda self, another: double(float(self._value)*float(another)),
	boolean: lambda self, another: double(float(self._value)*int(another))}

string.div_table={
	empty: lambda self, another: double(float(self._value)/0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self._value)/int(another)),
	double: lambda self, another: double(float(self._value)/float(another)),
	date: lambda self, another: double(float(self._value)/float(another)),
	string: lambda self, another: double(float(self._value)/float(another)),
	boolean: lambda self, another: double(float(self._value)/int(another))}

string.floordiv_table={
	empty: lambda self, another: integer(int(round(float(self._value)))//0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(round(float(self._value)))//int(another)),
	double: lambda self, another: integer(int(round(float(self._value)))//int(round(float(another)))),
	date: lambda self, another: integer(int(round(float(self._value)))//int(round(float(another)))),
	string: lambda self, another: integer(int(round(float(self._value)))//int(round(float(another)))),
	boolean: lambda self, another: integer(int(round(float(self._value)))//int(another))}

string.mod_table={
	empty: lambda self, another: integer(int(round(float(self._value)))%0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(round(float(self._value)))%int(another)),
	double: lambda self, another: integer(int(round(float(self._value)))%int(round(float(another)))),
	date: lambda self, another: integer(int(round(float(self._value)))%int(round(float(another)))),
	string: lambda self, another: integer(int(round(float(self._value)))%int(round(float(another)))),
	boolean: lambda self, another: integer(int(round(float(self._value)))%int(another))}

string.pow_table={
	empty: lambda self, another: double(float(self._value)**0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self._value)**int(another)),
	double: lambda self, another: double(float(self._value)**float(another)),
	date: lambda self, another: double(float(self._value)**float(another)),
	string: lambda self, another: double(float(self._value)**float(another)),
	boolean: lambda self, another: double(float(self._value)**int(another))}


string.eq_table={
	empty: lambda self, another: boolean(true) if self._value==u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self._value)==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self._value)==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self._value)==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value==unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==(u"True" if int(another)==true else u"False") else boolean(false)}

string.ne_table={
	empty: lambda self, another: boolean(true) if self._value!=u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self._value)!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self._value)!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self._value)!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value!=unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==(u"True" if int(another)==true else u"False") else boolean(false)}

string.lt_table={
	empty: lambda self, another: boolean(true) if self._value<u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self._value)<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self._value)<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self._value)<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value<unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==(u"True" if int(another)==true else u"False") else boolean(false)}

string.gt_table={
	empty: lambda self, another: boolean(true) if self._value>u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self._value)>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self._value)>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self._value)>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value>unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==(u"True" if int(another)==true else u"False") else boolean(false)}

string.le_table={
	empty: lambda self, another: boolean(true) if self._value<=u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self._value)<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self._value)<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self._value)<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value<=unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==(u"True" if int(another)==true else u"False") else boolean(false)}

string.ge_table={
	empty: lambda self, another: boolean(true) if self._value>=u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self._value)>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self._value)>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self._value)>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if self._value>=unicode(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if self._value==(u"True" if int(another)==true else u"False") else boolean(false)}


string.and_table={
	empty: lambda self, another: integer(int(self._value)&0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self._value)&int(another)),
	double: lambda self, another: integer(int(self._value)&int(round(float(another)))),
	date: lambda self, another: integer(int(round(float(self._value)))&int(round(float(another)))),
	string: lambda self, another: integer(int(self._value)&int(another)),
	boolean: lambda self, another: integer(int(self._value)&int(another))}

string.or_table={
	empty: lambda self, another: integer(int(self._value)|0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self._value)|int(another)),
	double: lambda self, another: integer(int(self._value)|int(round(float(another)))),
	date: lambda self, another: integer(int(round(float(self._value)))|int(round(float(another)))),
	string: lambda self, another: integer(int(self._value)|int(another)),
	boolean: lambda self, another: integer(int(self._value)|int(another))}

string.xor_table={
	empty: lambda self, another: integer(int(self._value)^0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self._value)^int(another)),
	double: lambda self, another: integer(int(self._value)^int(round(float(another)))),
	date: lambda self, another: integer(int(round(float(self._value)))^int(round(float(another)))),
	string: lambda self, another: integer(int(self._value)^int(another)),
	boolean: lambda self, another: integer(int(self._value)^int(another))}
