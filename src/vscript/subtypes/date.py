
import sys, re, datetime
from math import floor, ceil, fabs
from .. import errors, types


def encode_date(year, month, day, hours=0, minutes=0, seconds=0):
	date_value=float(datetime.date(year, month, day).toordinal()-693594)
	time_value=float(hours*60*60+minutes*60+seconds)/86400
	return date_value-time_value if date_value<0 else date_value+time_value

def decode_date(value):
	if value<0:
		time_value=fabs(value-ceil(value))
		date_value=int(value+time_value)
	else:
		time_value=value-floor(value)
		date_value=int(value-time_value)
	time_value=int(time_value * 86400)
	date_value=datetime.date.fromordinal(date_value+693594) # date_value is now python Date object
	seconds, time_value=time_value%60, time_value//60	
	minutes, time_value=time_value%60, time_value//60 # time_value is equal to hours after this	
	return date_value.year, date_value.month, date_value.day, time_value, minutes, seconds

def encode_time(hour, minute, second):
	return float(hour*60*60+minute*60+second)/86400


class date(object):

	__regex=re.compile("^(?:(?P<day>\d{1,2})[\.\-\/](?P<month>\d{1,2})(?:[\.\-\/](?P<year>\d{2,4}))?)?"\
		"(?:(?(day)\s+)(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(?::(?P<second>\d{1,2}))?(?:\s*(?P<ampm>(?:am|aM|Am|AM|pm|pM|Pm|PM)))?)?$")

	def __init__(self, value):
		if isinstance(value, int) or isinstance(value, float):
			self.value=value
		elif isinstance(value, str):
			match=self.__regex.match(value)
			if match:
				day=match.group("day")
				month=match.group("month")
				year=match.group("year") or unicode(datetime.datetime.today().year)
				hour=match.group("hour")
				minute=match.group("minute")
				second=match.group("second") or 0
				ampm=match.group("ampm")
				if len(year)==2:
					year="20"+year if year<"30" else "19"+year
				if day:
					day=int(day)
					month=int(month)
					year=int(year)
				else:
					day=1
					month=1
					year=1				
				if hour:
					hour=int(hour)
					minute=int(minute)
					second=int(second)
				else:
					hour=0
					minute=0
					second=0
				if ampm is not None:
					if hour>12:
						raise errors.invalid_date_format
					if ampm.lower()=="pm":
						hour+=12
						if hour==24:
							hour=0
				self.value=encode_date(year, month, day, hour, minute, second)
			else:
				raise errors.invalid_date_format
		else:
			raise errors.type_mismatch
				
	def __call__(self, *arguments, **keywords):
		raise errors.type_mismatch


	def get_type_code(self):
		return 7

	def get_type_name(self):
		return "Date"


	def check(self):
		return double(self.value) if self.value<-657434 or self.value>=2958466 else self


	def add_empty(self, another):
		return date(self.value+0)

	def sub_empty(self, another):
		return date(self.value-0)

	def mul_empty(self, another):
		return double(self.value*0)

	def div_empty(self, another):
		return double(self.value/0)

	def floordiv_empty(self, another):
		return integer(int(round(self.value))//0)

	def mod_empty(self, another):
		return integer(int(round(self.value))%0)

	def pow_empty(self, another):
		return double(self.value**0)


	def eq_empty(self, another):
		return boolean(v_true_value) if self.value==0 else boolean(v_false_value)

	def ne_empty(self, another):
		return boolean(v_true_value) if self.value!=0 else boolean(v_false_value)

	def lt_empty(self, another):
		return boolean(v_true_value) if self.value<0 else boolean(v_false_value)

	def gt_empty(self, another):
		return boolean(v_true_value) if self.value>0 else boolean(v_false_value)

	def le_empty(self, another):
		return boolean(v_true_value) if self.value<=0 else boolean(v_false_value)

	def ge_empty(self, another):
		return boolean(v_true_value) if self.value>=0 else boolean(v_false_value)


	def and_empty(self, another):
		return integer(int(round(self.value))&0)

	def or_empty(self, another):
		return integer(int(round(self.value))|0)

	def xor_empty(self, another):
		return integer(int(round(self.value))^0)


	def with_null(self, another):
		return v_null


	def and_null(self, another):
		return v_null

	def or_null(self, another):
		return v_null

	def xor_null(self, another):
		return v_null


	def add_integer(self, another):
		return date(self.value+another.value).check()

	def sub_integer(self, another):
		return date(self.value-another.value).check()

	def mul_integer(self, another):
		return double(self.value*another.value)

	def div_integer(self, another):
		return double(self.value/another.value)

	def floordiv_integer(self, another):
		return integer(int(round(self.value))//another.value)

	def mod_integer(self, another):
		return integer(int(round(self.value))%another.value)

	def pow_integer(self, another):
		return double(self.value**another.value)


	def eq_integer(self, another):
		return boolean(v_true_value) if self.value==another.value else boolean(v_false_value)

	def ne_integer(self, another):
		return boolean(v_true_value) if self.value!=another.value else boolean(v_false_value)

	def lt_integer(self, another):
		return boolean(v_true_value) if self.value<another.value else boolean(v_false_value)

	def gt_integer(self, another):
		return boolean(v_true_value) if self.value>another.value else boolean(v_false_value)

	def le_integer(self, another):
		return boolean(v_true_value) if self.value<=another.value else boolean(v_false_value)

	def ge_integer(self, another):
		return boolean(v_true_value) if self.value>=another.value else boolean(v_false_value)


	def and_integer(self, another):
		return integer(int(round(self.value))&another.value)

	def or_integer(self, another):
		return integer(int(round(self.value))|another.value)

	def xor_integer(self, another):
		return integer(int(round(self.value))^another.value)


	def add_double(self, another):
		return date(self.value+another.value).check()

	def sub_double(self, another):
		return date(self.value-another.value).check()

	def mul_double(self, another):
		return double(self.value*another.value)

	def div_double(self, another):
		return double(self.value/another.value)

	def floordiv_double(self, another):
		return integer(int(round(self.value))//int(round(another.value)))

	def mod_double(self, another):
		return integer(int(round(self.value))%int(round(another.value)))

	def pow_double(self, another):
		return double(self.value**another.value)


	def eq_double(self, another):
		return boolean(v_true_value) if self.value==another.value else boolean(v_false_value)

	def ne_double(self, another):
		return boolean(v_true_value) if self.value!=another.value else boolean(v_false_value)

	def lt_double(self, another):
		return boolean(v_true_value) if self.value<another.value else boolean(v_false_value)

	def gt_double(self, another):
		return boolean(v_true_value) if self.value>another.value else boolean(v_false_value)

	def le_double(self, another):
		return boolean(v_true_value) if self.value<=another.value else boolean(v_false_value)

	def ge_double(self, another):
		return boolean(v_true_value) if self.value>=another.value else boolean(v_false_value)


	def and_double(self, another):
		return integer(int(round(self.value))&int(round(another.value)))

	def or_double(self, another):
		return integer(int(round(self.value))|int(round(another.value)))

	def xor_double(self, another):
		return integer(int(round(self.value))^int(round(another.value)))


	def add_date(self, another):
		return date(self.value+another.value).check()

	def sub_date(self, another):
		return date(self.value-another.value).check()

	def mul_date(self, another):
		return double(self.value*another.value)

	def div_date(self, another):
		return double(self.value/another.value)

	def floordiv_date(self, another):
		return integer(int(round(self.value))//int(round(another.value)))

	def mod_date(self, another):
		return integer(int(round(self.value))%int(round(another.value)))

	def pow_date(self, another):
		return double(self.value**another.value)


	def eq_date(self, another):
		return boolean(v_true_value) if self.value==another.value else boolean(v_false_value)

	def ne_date(self, another):
		return boolean(v_true_value) if self.value!=another.value else boolean(v_false_value)

	def lt_date(self, another):
		return boolean(v_true_value) if self.value<another.value else boolean(v_false_value)

	def gt_date(self, another):
		return boolean(v_true_value) if self.value>another.value else boolean(v_false_value)

	def le_date(self, another):
		return boolean(v_true_value) if self.value<=another.value else boolean(v_false_value)

	def ge_date(self, another):
		return boolean(v_true_value) if self.value>=another.value else boolean(v_false_value)


	def and_date(self, another):
		return integer(int(round(self.value))&int(round(another.value)))

	def or_date(self, another):
		return integer(int(round(self.value))|int(round(another.value)))

	def xor_date(self, another):
		return integer(int(round(self.value))^int(round(another.value)))


	def add_string(self, another):
		return date(self.value+float(another.value)).check()

	def sub_string(self, another):
		return date(self.value+float(another.value)).check()

	def mul_string(self, another):
		return double(self.value*float(another.value))

	def div_string(self, another):
		return double(self.value/float(another.value))

	def floordiv_string(self, another):
		return integer(int(round(self.value))//int(round(float(another.value))))

	def mod_string(self, another):
		return integer(int(round(self.value))%int(round(float(another.value))))

	def pow_string(self, another):
		return double(self.value**float(another.value))


	def eq_string(self, another):
		return boolean(v_true_value) if self.value==int(another.value) else boolean(v_false_value)

	def ne_string(self, another):
		return boolean(v_true_value) if self.value!=int(another.value) else boolean(v_false_value)

	def lt_string(self, another):
		return boolean(v_true_value) if self.value<int(another.value) else boolean(v_false_value)

	def gt_string(self, another):
		return boolean(v_true_value) if self.value>int(another.value) else boolean(v_false_value)

	def le_string(self, another):
		return boolean(v_true_value) if self.value<=int(another.value) else boolean(v_false_value)

	def ge_string(self, another):
		return boolean(v_true_value) if self.value>=int(another.value) else boolean(v_false_value)


	def and_string(self, another):
		return integer(int(round(self.value))&int(another.value))

	def or_string(self, another):
		return integer(int(round(self.value))|int(another.value))

	def xor_string(self, another):
		return integer(int(round(self.value))^int(another.value))


	def add_boolean(self, another):
		result=data(self.value+another.value).check()

	def sub_boolean(self, another):
		result=data(self.value-another.value).check()

	def mul_boolean(self, another):
		return double(self.value*another.value)

	def div_boolean(self, another):
		return double(self.value/another.value)

	def floordiv_boolean(self, another):
		return integer(int(round(self.value))//another.value)

	def mod_boolean(self, another):
		return integer(int(round(self.value))%another.value)

	def pow_boolean(self, another):
		return double(self.value**another.value)


	def eq_boolean(self, another):
		return boolean(v_true_value) if self.value==another.value else boolean(v_false_value)

	def ne_boolean(self, another):
		return boolean(v_true_value) if self.value!=another.value else boolean(v_false_value)

	def lt_boolean(self, another):
		return boolean(v_true_value) if self.value<another.value else boolean(v_false_value)

	def gt_boolean(self, another):
		return boolean(v_true_value) if self.value>another.value else boolean(v_false_value)

	def le_boolean(self, another):
		return boolean(v_true_value) if self.value<=another.value else boolean(v_false_value)

	def ge_boolean(self, another):
		return boolean(v_true_value) if self.value>=another.value else boolean(v_false_value)


	def and_boolean(self, another):
		return integer(int(round(self.value))&another.value)

	def or_boolean(self, another):
		return integer(int(round(self.value))|another.value)

	def xor_boolean(self, another):
		return integer(int(round(self.value))^another.value)


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
			return date.add_table.get(type(another), date.add_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __sub__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return date.sub_table.get(type(another), date.sub_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __mul__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return date.mul_table.get(type(another), date.mul_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback

	def __div__(self, another):
		if isinstance(another, (types.function, types.method, generic)):
			another=another()
		try:
			return date.div_table.get(type(another), date.div_unknown)(self, another)
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
			return date.floordiv_table.get(type(another), date.floordiv_unknown)(self, another)
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
			return date.mod_table.get(type(another), date.mod_unknown)(self, another)
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
			return date.pow_table.get(type(another), date.pow_unknown)(self, another)
		except OverflowError, error:
			exclass, exexception, extraceback=sys.exc_info()
			raise errors.overflow, None, extraceback


	def __eq__(self, another):
		return date.eq_table.get(type(another), date.eq_unknown)(self, another)

	def __ne__(self, another):
		return date.ne_table.get(type(another), date.ne_unknown)(self, another)

	def __lt__(self, another):
		return date.lt_table.get(type(another), date.lt_unknown)(self, another)

	def __gt__(self, another):
		return date.gt_table.get(type(another), date.gt_unknown)(self, another)

	def __le__(self, another):
		return date.le_table.get(type(another), date.le_unknown)(self, another)

	def __ge__(self, another):
		return date.ge_table.get(type(another), date.ge_unknown)(self, another)

	def __hash__(self):
		return hash(self.value)
	
	def __and__(self, another):
		return date.and_table.get(type(another), date.and_unknown)(self, another)

	def __or__(self, another):
		return date.or_table.get(type(another), date.or_unknown)(self, another)

	def __xor__(self, another):
		return date.xor_table.get(type(another), date.xor_unknown)(self, another)

	def __invert__(self):
		raise integer(~int(round(self.value)))
		
	def __neg__(self):
		return double(-self.value)

	def __pos__(self):
		return double(+self.value)

	def __abs__(self):
		return double(fabs(self.value))

	def __int__(self):
		return int(round(self.value))

	def __float__(self):
		return self.value

	def __str__(self):
		year, month, day, hour, minute, second=decode_date(self.value)
		if hour+minute+second:
			return "%02d.%02d.%d %02d:%02d:%02d"%(day, month, year, hour, minute, second)
		else:
			return "%02d.%02d.%d"%(day, month, year)

	def __unicode__(self):
		year, month, day, hour, minute, second=decode_date(self.value)
		if hour+minute+second:
			return u"%02d.%02d.%d %02d:%02d:%02d"%(day, month, year, hour, minute, second)
		else:
			return u"%02d.%02d.%d"%(day, month, year)
	
	def __nonzero__(self):
		return bool(self.value)

	def __repr__(self):
		return "DATE@%s:%s"%(object.__repr__(self)[-9:-1], repr(self.value))


from .null import null, v_null
from .integer import integer
from .double import double, nan, infinity
from .boolean import boolean, v_true_value, v_false_value
from .generic import generic
