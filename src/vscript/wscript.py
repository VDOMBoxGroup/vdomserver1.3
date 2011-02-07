
import errors, types

from array import array
from empty import empty, v_empty
from null import null, v_null
from integer import integer
from double import double, nan, infinity
from date import date
from string import string
from boolean import boolean, v_true_value, v_false_value
from generic import generic
from nothing import nothing, v_nothing
from variant import variant
from constant import constant
from shadow import shadow
from binary import binary

from . import byref, byval
from auxiliary import as_value, as_is, as_array, as_integer, as_double, as_string, as_boolean, as_generic, as_date, as_binary
from auxiliary import pack, unpack, adapt



class v_wscript(generic):

	def v_version(self):
		return string(u"VDOM VScript (Beta)")

	def v_echo(self, *arguments):
		debug(" ".join([unicode(as_value(argument)) for argument in arguments]), console=True)



v_wscript=v_wscript()
