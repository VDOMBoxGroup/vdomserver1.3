
from ..subtypes import generic, string


class v_wscript(generic):

	def v_version(self):
		return string(u"VDOM VScript (Beta)")

	def v_echo(self, *arguments):
		debug(" ".join([unicode(argument.as_simple) for argument in arguments]), console=True)


v_wscript=v_wscript()
