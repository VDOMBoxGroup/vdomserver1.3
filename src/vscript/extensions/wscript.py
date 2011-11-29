
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *


class v_wscript(generic):

	def v_version(self):
		return string(u"VDOM VScript (Beta)")

	def v_echo(self, *arguments):
		debug(" ".join([unicode(as_value(argument)) for argument in arguments]), console=True)


v_wscript=v_wscript()
