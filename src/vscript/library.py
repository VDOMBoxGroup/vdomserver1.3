
import random, datetime, re

import errors, types

from array import array
from empty import empty, v_empty
from null import null, v_null
from integer import integer
from double import double, nan, infinity
from date import date, decode_date, encode_date, encode_time
from string import string
from boolean import boolean, v_true_value, v_false_value
from generic import generic
from nothing import nothing, v_nothing
from variant import variant
from constant import constant
from shadow import shadow

from . import byref, byval
from auxiliary import as_value, as_is, as_array, as_integer, as_double, as_string, as_boolean, as_generic, as_date, as_date

from calendar import weekday, Calendar, month_name, month_abbr, day_name, day_abbr

import version



__all__=["v_array", "v_subarray", "v_filter", "v_lbound", "v_ubound", "v_join",
	"v_abs", "v_sgn", "v_hex", "v_oct", "v_chr",
	"v_asc", "v_escape", "v_unescape", "v_lcase", "v_ucase", "v_instr", "v_instrrev",
	"v_len", "v_left", "v_right", "v_trim", "v_ltrim", "v_rtrim", "v_mid", "v_replace",
	"v_space", "v_strcomp", "v_string", "strreverse", "v_split",
	"v_exp", "v_int", "v_fix", "v_log", "v_rnd", "v_round", "v_sqr",
	"v_atn", "v_cos", "v_sin", "v_tan",
	"v_cbool", "v_cdate", "v_csng", "v_cdbl", "v_cbyte", "v_cint", "v_clng", "v_cstr",
	"v_date", "v_dateadd", "v_datediff", "v_datepart", "v_dateserial", "v_datevalue",
	"v_day", "v_hour", "v_minute", "v_month", "v_monthname", "v_now", "v_second", "v_time", 
	"v_timer", "v_timeserial", "v_timevalue", "v_weekday", "v_weekdayname", "v_year", 
	"v_vartype", "v_typename",
	"v_isarray", "v_isdate", "v_isempty", "v_isnull", "v_isnothing", "v_isnumeric", "v_isobject",
	"v_rgb",
	"v_scriptengine", "v_scriptenginebuildversion",
	"v_scriptenginemajorversion", "v_scriptengineminorversion"]



def ireplace(s1, s2, s3, count=0):
	pattern=re.compile(re.escape(s2), re.I)
	return re.sub(pattern, s3, s1, count)

def get_week_count(firstdayofweek, firstweekofyear, year, month, day):
	cl = Calendar(firstdayofweek)
	data = cl.monthdayscalendar(year, 1)
	week_cnt = 0
	day_cnt = 0
	# counting for first month
	for i in range(0, 7):
		if data[0][i] != 0:
			day_cnt += 1
	if (firstweekofyear == 2 and day_cnt < 4) or (firstweekofyear == 3 and day_cnt < 7):
		week_cnt = -1
	if month != 1:		
		week_cnt += len(data)
		if data[len(data)-1][6] == 0:
			week_cnt -= 1
		#counting for other monthes
		for m in range(2, month):
			data = cl.monthdayscalendar(year, m)
			week_cnt += len(data)
			if data[len(data)-1][6] == 0:
				week_cnt -= 1
	#here we have week count in week_cnt before current month
	data = cl.monthdayscalendar(year, month)	
	for week in range(0, len(data)):
		week_cnt += 1
		if day in data[week]:
			break
	return week_cnt

def is_leap_year(year):
	return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
 
def max_dayin_month(year, month):
	if month in (4, 6, 9, 11):
		return 30
	elif month==2 and is_leap_year(year):
		return 29
	elif month==2:
		return 28
	else:
		return 31

def inc_month(year, month, day, cnt):
	""" Increments/Decrements month on cnt, adjusting date correspondingly """
	month += cnt
	if month > 12 or month < 0:
		year += month // 12
		month = month % 12
	elif month == 0:
		year -= 1
		month = 12		
	return year, month, min(day, max_dayin_month(year, month))

def inc_day(year, month, day, cnt):
	""" Increments/Decrements day on cnt, adjusting date correspondingly """
	day += cnt
	ymMax = max_dayin_month(year, month)
	while not day in range(1, ymMax+1):
		if day > 0:
			day -= ymMax
			month += 1
			if month > 12:
				year += 1
				month = 1
		elif day < 0:
			day += ymMax
			month -= 1
			if month < 1:
				year -= 1
				month = 12
		else:
			month -= 1
			if month < 1:
				year -= 1
				month = 12
			day = max_dayin_month(year, month)
		ymMax = max_dayin_month(year, month)	
	return year, month, day

def inc_hour(year, month, day, hour, cnt):
	""" Increments/Decrements hour on cnt, adjusting date correspondingly """
	hour += cnt
	if not hour in range(1, 25):	
		daydiff, hour = hour // 24, hour % 24
		year, month, day = inc_day(year, month, day, daydiff)
	return year, month, day, hour

def inc_minute(year, month, day, hour, minute, cnt):
	""" Increments/Decrements minute on cnt, adjusting date and time correspondingly """
	minute += cnt
	if not minute in range(1, 61):
		hourdiff, minute = minute // 60, minute % 60
		year, month, day, hour = inc_hour(year, month, day, hour, hourdiff)
	return year, month, day, hour, minute
  
def inc_second(year, month, day, hour, minute, second, cnt):
	""" Increments/Decrements second on cnt, adjusting date and time correspondingly """
	second += cnt
	if not second in range(1, 61):
		mindiff, second = second // 60, second % 60
		year, month, day, hour, minute = inc_minute(year, month, day, hour, minute, mindiff)
	return year, month, day, hour, minute, second



def v_array(*arguments):
	values=[]
	for value in arguments:
		values.append(as_value(value))
	return array(values=values)

def v_subarray(value, *indexes):
	return as_array(value).subarray(*indexes)

def v_filter(strings, value, include=None, compare=None):
	strings, value=as_array(strings), as_string(value)
	include=False if include is None else as_boolean(include)
	compare=0 if compare is None else as_integer(compare)
	if compare<0 or compare>1:
		raise errors.invalid_procedure_call(name="filter")
	values=[]
	search_string=value.lower() if compare else value
	for vstring in strings:
		current_string=vstring.value.lower() if compare else vstring.value
		if include and current_string.find(search_string)>=0 or \
			not include and current_string.find(search_string)<0:
			values.append(vstring)
	return array(values=values)

def v_lbound(arrayname, dimension=None):
	arrayname=as_array(arrayname)
	dimension=0 if dimension is None else as_integer(dimension)-1
	if dimension<0 or dimension>=len(arrayname.subscripts):
		raise errors.subscript_out_of_range
	return integer(0)

def v_ubound(arrayname, dimension=None):
	arrayname=as_array(arrayname)
	dimension=0 if dimension is None else as_integer(dimension)-1
	if dimension<0 or dimension>=len(arrayname.subscripts):
		raise errors.subscript_out_of_range
	return integer(arrayname.subscripts[dimension])

def v_join(list, delimiter=None):
	list=as_array(list)
	delimiter=u" " if delimiter is None else as_string(delimiter)
	return string(delimiter.join([as_string(item) for item in list]))



def v_abs(number):
	return integer(abs(as_integer(number)))

def v_sgn(number):
	number=as_integer(number)
	return integer(-1 if number<0 else 1 if number>0 else 0)

def v_hex(number):
	number=as_integer(number)
	string1=hex(number)[2:] if number>0 else \
		hex(0x100000000+number)[2:-1] if number<-0xFFFF else \
		hex(0x10000+number)[2:] if number<0 else "0"
	return string(unicode(string1.upper()))

def v_oct(number):
	number=as_integer(number)
	string1=oct(number)[1:] if number>0 else \
		oct(0x100000000+number)[1:-1] if number<-0xFFFF else \
		oct(0x10000+number)[1:] if number<0 else "0"
	return string(unicode(string1))

def v_chr(number):
	return string(unichr(as_integer(number)))



def v_asc(string1):
	string1=as_string(string1)
	if len(string1)<1:
		raise errors.invalid_procedure_call(name=u"asc")
	return integer(ord(string1[0]))

def v_escape(string1):
	return string(escape(as_string(string1)))

def v_unescape(string1):
	return string(unescape(as_string(string1)))

def v_lcase(string1):
	return string(as_string(string1).lower())

def v_ucase(string1):
	return string(as_string(string1).upper())

def v_instr(string1, string2, start=None, compare=None): # start, string1, string2
	if start is None:
		string1, string2, start=as_string(string1), as_string(string2), 0
	else:
		string1, string2, start=as_string(string2), as_string(start), as_integer(string1)-1
		if start<0:
			raise errors.invalid_procedure_call(name=u"instr")
	compare=0 if compare is None else as_integer(compare)
	if compare<0 or compare>1:
		raise errors.invalid_procedure_call(name=u"instr")
	if string1 is v_null or string2 is v_null:
		return v_null
	if compare:
		return integer(as_string(string1).lower().find(as_string(string2).lower(), start)+1)
	else:
		return integer(as_string(string1).find(as_string(string2), start)+1)

def v_instrrev(string1, string2, start=None, compare=None):
	if start is None:
		string1, string2, start=as_string(string1), as_string(string2), -1
	else:
		string1, string2, start=as_string(string1), as_string(string2), as_integer(start)-1
		if start==-2:
			start=-1
		elif start<0:
			raise errors.invalid_procedure_call(name=u"instrrev")
	compare=0 if compare is None else as_integer(compare)
	if compare<0 or compare>1:
		raise errors.invalid_procedure_call(name=u"instrrev")
	if string1 is v_null or string2 is v_null:
		return v_null
	if compare:
		return integer(as_string(string1).lower().rfind(as_string(string2).lower(), start)+1)
	else:
		return integer(as_string(string1).rfind(as_string(string2), start)+1)
	
def v_len(string1):
	return integer(len(as_string(string1)))

def v_left(string1, length):
	length=as_integer(length)
	if length<0:
		raise errors.invalid_procedure_call(name=u"left")
	return string(as_string(string1)[0:length])

def v_right(string1, length):
	length=as_integer(length)
	if length<0:
		raise errors.invalid_procedure_call(name=u"right")
	return string(as_string(string1)[-length:])

def v_trim(string1):
	return string(as_string(string1).strip())

def v_ltrim(string1):
	return string(as_string(string1).lstrip())

def v_rtrim(string1):
	return string(as_string(string1).rstrip())

def v_mid(string1, start, length=None):
	start=as_integer(start)-1
	if start<0:
		raise errors.invalid_procedure_call(name=u"mid")
	if length is None:
		return string(as_string(string1)[start:])
	else:
		length=as_integer(length)
		if length<0:
			raise errors.invalid_procedure_call(name=u"mid")
		return string(as_string(string1)[start:start+length])

def v_replace(expression, find, replacewith, start=None, count=None, compare=None):
	expression=as_string(expression)
	find, replacewith=as_string(find), as_string(replacewith)
	start=0 if start is None else as_integer(start)-1
	if start<0:
		raise errors.invalid_procedure_call(name=u"replace")
	compare=0 if compare is None else as_integer(compare)
	if compare<0 or compare>1:
		raise errors.invalid_procedure_call(name=u"replace")
	if count is None:
		if compare:
			return string(ireplace(expression[start:], find, replacewith))
		else:
			return string(expression[start:].replace(find, replacewith))
	else:
		count=as_integer(count)
		if count<0:
			raise errors.invalid_procedure_call(name=u"replace")
		if compare:
			return string(ireplace(expression[start:], find, replacewith, count))
		else:
			return string(expression[start:].replace(find, replacewith, count))



def v_space(number):
	number=as_integer(number)
	if number<0:
		raise errors.invalid_procedure_call(name=u"space")
	return string(u" "*number)

def v_strcomp(string1, string2, compare=None):
	string1, string2=as_string(string1), as_string(string2)
	compare=0 if compare is None else as_integer(compare)
	if compare<0 or compare>1:
		raise errors.invalid_procedure_call(name=u"strcomp")
	if string1 is v_null or string2 is v_null:
		return v_null
	if compare:
		return integer(cmp(string1.lower(), string2.lower()))
	else:
		return integer(cmp(string1, string2))

def v_string(number, character):
	number=as_integer(number)
	if character is v_null:
		return v_null
	if isinstance(character, integer):
		number=as_integer(number)
		if number<0 or number>255:
			raise errors.invalid_procedure_call(name=u"string")
		return string(chr(character)*number)
	elif isinstance(character, string):
		character=as_string(character)
		if len(character)<1:
			raise errors.invalid_procedure_call(name=u"string")
		return string(character[0]*number)
	else:
		raise errors.type_mismatch

def strreverse(string1):
	return string(as_string(string1)[::-1])

def v_split(expression, delimiter=None, count=None, compare=None):
	delimiter=u" " if delimiter is None else as_string(delimiter)
	count=-1 if count is None else as_integer(count)
	if count<-1:
		raise errors.invalid_procedure_call(name=u"split")
	compare=0 if compare is None else as_integer(compare)
	if compare<0 or compare>1:
		raise errors.invalid_procedure_call(name=u"split")
	if compare:
		strings=ireplace(as_string(expression), delimiter,
			delimiter.lower()).split(delimiter.lower())
	else:
		strings=as_string(expression).split(delimiter)
	if count>-1:
		strings=strings[:count+1]
	values=[]
	for string1 in strings:
		values.append(string(string1))
	return array(values=values)



def v_exp(number):
	number=as_double(number)
	# 709.782712893 - highest value from MSDN
	if number>709.782712893:
		raise errors.invalid_procedure_call(name=u"exp")
	return double(math.exp(number))

def v_int(number):
	number=as_double(number)
	return integer(math.floor(number))
	
def v_fix(number):
	number=as_double(number)
	return integer(math.ceil(number))

def v_log(number):
	number=as_double(number)
	if number<=0:
		raise errors.invalid_procedure_call(name=u"log")
	return double(math.log(number))



last_random=random.random()

def v_rnd(number=None):
	global last_random
	number=1 if number is None else as_double(number)
	if number<0:
		random.seed(number)
		value=random.random()
	elif number>0:
		value=random.random()
	else:
		value=last_random
	last_random=value
	return double(value)

def v_round(number):
	number=as_double(number)
	return double(round(number))

def v_sqr(number):
	number=as_double(number)
	if number<0:
		raise errors.invalid_procedure_call(name=u"sqr")
	return double(math.sqrt(number))



def v_atn(number):
	number=as_double(number)
	return double(math.atan(number))

def v_cos(number):
	number=as_double(number)
	return double(math.cos(number))

def v_sin(number):
	number=as_double(number)
	return double(math.sin(number))

def v_tan(number):
	number=as_double(number)
	return double(math.tan(number))



def v_cbool(expression):
	return boolean(bool(as_value(expression)))

def v_cdate(expression):
	return date(expression)

def v_csng(expression):
	return double(float(expression))

def v_cdbl(expression):
	return double(float(expression))

def v_cbyte(expression):
	value=integer(int(as_value(expression)))
	if value<0:
		raise errors.invalid_procedure_call(name=u"cbyte")
	return value

def v_cint(expression):
	return integer(int(as_value(expression)))

def v_clng(expression):
	return integer(int(as_value(expression)))

def v_cstr(expression):
	return string(unicode(as_value(expression)))



def v_date():
	return date(datetime.datetime.today().toordinal()-693594)

def v_dateadd(interval, number, vbdate):
	interval=as_string(interval)
	number=as_integer(number)
	value=as_date(vbdate)
	year, month, day, hour, minute, second=decode_date(value)
	dt_value=datetime.datetime(year, month, day, hour, minute, second)
	if interval==u"yyyy":
		year+=number
		day=min(max_dayin_month(year, month), day)
	elif interval==u"q":		
		year, month, day=inc_month(year, month, day, number*3)		
	elif interval==u"m":
		year, month, day=inc_month(year, month, day, number)		
	elif interval==u"y":
		year, month, day=inc_day(year, month, day, number)
	elif interval==u"d":		
		year, month, day=inc_day(year, month, day, number)
	elif interval==u"w":		
		year, month, day=inc_day(year, month, day, number)
	elif interval==u"ww":		
		year, month, day=inc_day(year, month, day, number*7)
	elif interval==u"h":
		year, month, day, hour=inc_hour(year, month, day, hour, number)
	elif interval==u"n":
		year, month, day, hour, minute=inc_minute(year, month, day, hour, minute, number)
	elif interval==u"s":
		year, month, day, hour, minute, second=inc_second(year, month, day, hour, minute, second, number)
	else:
		raise errors.invalid_procedure_call(name=u"dateadd")
	return date(encode_date(year, month, day, hour, minute, second)).check()
  
# didnt understand the use of "firstweekofyear" parameter

def v_datediff(interval, vbdate1, vbdate2, firstdayofweek=None, firstweekofyear=None):
	interval=as_string(interval)
	value1, value2=as_date(vbdate1), as_date(vbdate2)
	firstdayofweek=1 if firstdayofweek is None else as_integer(firstdayofweek)
	firstweekofyear=1 if firstweekofyear is None else as_integer(firstweekofyear)
	year1, month1, day1, hour1, minute1, second1=decode_date(value1)
	year2, month2, day2, hour2, minute2, second2=decode_date(value1)
	sign=1 if value1>=value2 else -1
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"datediff")
	if interval==u"yyyy":
		return integer(year2-year1)
	elif interval==u"q":
		q1=(month1-1)//3+1 # getting quarter of first date
		q2=(month2-1)//3+1 # getting quarter of second date
		return integer(q2-q1+(year2-year1)*4)
	elif interval==u"m":
		return integer(month2-month1+(year2-year1)*12)
	elif interval==u"y":
		return integer(int(value2)-int(value1))
	elif interval==u"d":
		return integer(int(value2)-int(value1))
	elif interval==u"w":
		days=math.fabs(int(value2)-int(value1))
		return integer((days//7)*sign)
	elif interval==u"ww":
		days=math.fabs(int(value2)-int(value1))
		wd=weekday(year1, month1, day1)+2 if sign==1 else weekday(year2, month2, day2)+2
		wd=1 if wd==8 else wd
		days+=wd-firstdayofweek
		return integer(days)//7*sign
	elif interval==u"h":
		s2=1 if value2>=0 else -1
		s1=1 if value1>=0 else -1
		d2=math.fabs(value2*86400)//3600*s2
		d1=math.fabs(value1*86400)//3600*s1
		return integer(d2-d1)
	elif interval==u"n":
		s2=1 if value2>=0 else -1
		s1=1 if value1>=0 else -1
		d2=math.fabs(value2*86400)//60*s2
		d1=math.fabs(value1*86400)//60*s1
		return integer(d2-d1)
	elif interval==u"s":
		return integer(int((value2-value1)*86400))
	else:
		raise errors.invalid_procedure_call(name=u"datediff")

def v_datepart(interval, vbdate, firstdayofweek=None, firstweekofyear=None):
	interval=as_string(interval)
	value=as_date(vbdate)
	firstdayofweek=1 if firstdayofweek is None else as_integer(firstdayofweek)
	firstweekofyear=1 if firstweekofyear is None else as_integer(firstweekofyear)
	year, month, day, hour, minute, second=decode_date(value)
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"datepart")
	if firstweekofyear<1 or firstweekofyear>3:
		raise errors.invalid_procedure_call(name=u"datepart")
	if interval==u"yyyy":
		return integer(year)
	elif interval==u"q":
		return integer((month-1)//3+1)
	elif interval==u"m":
		return integer(month)
	elif interval==u"y":
		for i in range(1, month):
			days+=max_dayin_month(year, i)
		return integer(day+days)
	elif interval==u"d":
		return integer(day)
	elif interval==u"w":
		wd=weekday(year, month, day)+2
		wd=1 if wd==8 else wd
		return integer(wd)
	elif interval==u"ww":
		wd=firstdayofweek-2
		wd=6 if wd==-1 else wd
		week_cnt=get_week_count(wd, firstweekofyear, year, month, day)
		if week_cnt==0:
			week_cnt=get_week_count(wd, firstweekofyear, year-1, 12, 31)
		return integer(week_cnt)
	elif interval==u"h":
		return integer(hour)
	elif interval==u"n":
		return integer(minute)
	elif interval==u"s":
		return integer(second)
	else:
		raise errors.invalid_procedure_call(name=u"datepart")
  
def v_dateserial(year, month, day):
	year=as_integer(year)
	month=as_integer(month)
	day=as_integer(day)
	if year<0 or year>9999:
		raise errors.invalid_procedure_call(name=u"dateserial")
	if year<100:
		year+=1900
	if month<1 or month>12:
		year, month, d=inc_month(year, month, 1, 0)
	if day<1 or day>max_dayin_month(year, month):
		year, month, day=inc_day(year, month, day, 0)
	return date(encode_date(year, month, day))

def v_datevalue(vbdate):
	value=as_date(vbdate);
	year, month, day, hour, minute, second=decode_date(value)
	return date(encode_date(year, month, day))

def v_day(vbdate):
	value=as_date(vbdate);
	year, month, day, hour, minute, second=decode_date(value)
	return integer(day)

def v_hour(vbdate):
	value=as_date(vbdate);
	year, month, day, hour, minute, second=decode_date(value)
	return integer(hour)

def v_minute(vbdate):
	value=as_date(vbdate);
	year, month, day, hour, minute, second=decode_date(value)
	return integer(minute)

def v_month(vbdate):
	value=as_date(vbdate);
	year, month, day, hour, minute, second=decode_date(value)
	return integer(month)

def v_monthname(month, abbreviate=None):
	month=as_integer(month)
	abbreviate=False if abbreviate is None else as_boolean(abbreviate)
	if month<1 or month>12:
		raise errors.invalid_procedure_call(name=u"monthname")
	return string(month_abbr[month]) if abbreviate else string(month_name[month])

def v_now():
	dt=datetime.datetime.today()
	return date(encode_date(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))

def v_second(vbdate):
	value=as_date(vbdate);
	year, month, day, hour, minute, second=decode_date(value)
	return integer(second)
	
def v_time():
	dt=datetime.datetime.today()
	return date(encode_time(dt.hour, dt.minute, dt.second))

def v_timer():
	dt=datetime.datetime.today()
	return integer(dt.hour*3600+dt.minute*60+dt.second)

def v_timeserial(hour, minute, second):
	hour=as_integer(hour)
	minute=as_integer(minute)
	second=as_integer(second)
	if hour<0 or hour>23:
		raise errors.invalid_procedure_call(name=u"timeserial")
	return date(encode_time(hour, minute, second))

def v_timevalue(vbtimevalue):
	value=as_value(vbtimevalue)
	if isinstance(value, integer):
		value=as_integer(value)
	elif isinstance(value, string):
		value=as_string(value)
	else:
		 errors.invalid_procedure_call(name=u"timevalue")
	vbtime=date(value)
	if vbtime.value>0: # TODO: Something strange!
		vbtime.value-=floor(vbtime.value)
	else:
		vbtime.value=fabs(vbtime.value-ceil(vbtime.value))
	return vbtime

def v_weekday(vbdate, firstdayofweek=None):
	value=as_date(vbdate);
	firstdayofweek=1 if firstdayofweek is None else as_integer(firstdayofweek)
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"weekday")
	year, month, day, hour, minute, second=decode_date(value)
	wd=datetime.date(year, month, day).weekday()+2
	wd=1 if wd==8 else wd
	result=wd-firstdayofweek+1
	result=7+result if result<0 else result # TODO: Something strange!
	return result

def v_weekdayname(weekday, abbreviate=None, firstdayofweek=None):
	weekday=as_integer(weekday)
	firstdayofweek=1 if firstdayofweek is None else as_integer(firstdayofweek)
	abbreviate=False if abbreviate is None else as_boolean(abbreviate)
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"weekday")
	result=weekday+firstdayofweek-1
	result=result-7 if result>7 else result	
	result-=2
	result=6 if result==-1 else result	
	return string(day_abbr[result]) if abbreviate else string(day_name[result])

def v_year(vbdate):
	value=as_date(vbdate);
	year, month, day, hour, minute, second=decode_date(value)
	return integer(year)



def v_vartype(value):
	value=as_is(value)
	return integer(value.get_type_code())

def v_typename(value):
	value=as_is(value)
	return integer(value.get_type_name())



def v_isarray(value):
	value=as_is(value)
	return v_true_value if isinstance(value, array) else v_false_value
	
def v_isdate(value):
	value=as_is(value)
	return v_true_value if isinstance(value, date) else v_false_value

def v_isempty(value):
	value=as_is(value)
	return v_true_value if isinstance(value, empty) else v_false_value
	
def v_isnull(value):
	value=as_is(value)
	return v_true_value if isinstance(value, null) else v_false_value
	
def v_isnothing(value):
	value=as_is(value)
	return v_true_value if isinstance(value, nothing) else v_false_value
	
def v_isnumeric(value):
	value=as_is(value)
	return v_true_value if isinstance(value, (integer, double)) else v_false_value
	
def v_isobject(value):
	value=as_is(value)
	return v_true_value if isinstance(value, generic) else v_false_value



def v_rgb(red, green, blue):
	red, green, blue=as_number(red), as_number(green), as_number(blue)
	return integer(blue+(green*256)+(red*65535))



def v_scriptengine():
	return string(u"VScript")

def v_scriptenginebuildversion():
	return integer(version.build)

def v_scriptenginemajorversion():
	return integer(version.major)

def v_scriptengineminorversion():
	return integer(version.minor)
