
import re

import managers

from util.imaging import VDOM_imaging

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



def as_rgb(value):
	value=as_integer(value)
	blue=value%256
	green=value//256%256
	red=value//65535
	return red, green, blue



class v_vdomimaging(generic):

	def __init__(self):
		generic.__init__(self)
		self.__application_id=managers.request_manager.current.application_id
		self.__imaging=VDOM_imaging()

	def v_load(self, resource_id):
		self.__imaging.load(self.__application_id, as_string(resource_id))

	def v_createfont(self, *arguments):
		adaptors=(("name", as_string), ("size", as_integer), ("color", as_string),
			("fontstyle", as_string), ("fontweight", as_string))
		self.__imaging.create_font(**adapt(arguments, adaptors, name="createfont"))

	def v_writetext(self, *arguments):
		adaptors=(("text", as_string), ("color", as_rgb), ("align", as_string),
			("ident", as_integer), ("textdecoration", as_string))
		self.__imaging.write_text(**adapt(arguments, adaptors, require=1, name="writetext"))
	
	def v_crop(self, x, y, w, h):
		self.__imaging.crop(as_integer(x), as_integer(y), as_integer(w), as_integer(h))
		
	def v_thumbnail(self, size):
		self.__imaging.thumbnail(as_integer(size))

	def v_savetemporary(self, label, *arguments):
		adaptors=(("format", as_string))
		id=self.__imaging.save_temporary(self.__application_id, None,
			as_string(label), **adapt(arguments, adaptors))
		return string(id)

	def v_save(self, name, *arguments):
		adaptors=(("format", as_string))
		id=self.__imaging.save(self.__application_id, as_string(name),
			**adapt(arguments, adaptors))
		return string(id)

	def v_width(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("width")
		else:
			width, height=self.__imaging.size
			return integer(width)

	def v_height(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("height")
		else:
			width, height=self.__imaging.size
			return integer(height)
