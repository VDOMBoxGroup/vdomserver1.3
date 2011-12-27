
from json import JSONDecoder, JSONEncoder
from json.scanner import py_make_scanner
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *
from .dictionary import v_dictionary



default_decoder=JSONDecoder()

default_parse_float=default_decoder.parse_float
default_parse_int=default_decoder.parse_int
default_parse_constant=default_decoder.parse_constant
default_parse_object=default_decoder.parse_object
default_parse_array=default_decoder.parse_array
default_parse_string=default_decoder.parse_string



def vscript_parse_float(*arguments):
	return double(default_parse_float(*arguments))

def vscript_parse_int(*arguments):
	return integer(default_parse_int(*arguments))

def vscript_parse_constant(*arguments):
	return double(default_parse_constant(*arguments))

def vscript_parse_object(*arguments):
	obj, end=default_parse_object(*arguments)
	return v_dictionary(obj), end

def vscript_parse_array(*arguments):
	obj, end=default_parse_array(*arguments)
	return array(obj), end

def vscript_parse_string(*arguments):
	obj, end=default_parse_string(*arguments)
	return string(obj), end



class VScriptDecoder(JSONDecoder):

	def __init__(self, *arguments, **keywords):
		JSONDecoder.__init__(self, *arguments, **keywords)
		self.parse_float=vscript_parse_float
		self.parse_int=vscript_parse_int
		self.parse_constant=vscript_parse_constant
		self.parse_object=vscript_parse_object
		self.parse_array=vscript_parse_array
		self.parse_string=vscript_parse_string
		self.scan_once=py_make_scanner(self)

class VScriptEncoder(JSONEncoder):

	def default(self, object):
		if isinstance(object, (double, integer, string, array, v_dictionary)):
			return object.value
		else:
			return JSONEncoder.default(self, object)



def v_asjson(value):
	return VScriptDecoder().decode(as_string(value))

def v_tojson(value):
	return VScriptEncoder().encode(as_value(value))
