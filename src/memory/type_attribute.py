"""XML type attribute module"""

class VDOM_type_attribute:
	"""XML type attribute class"""

	def __init__(self, name, default_value):
		"""constructor"""
		self.name = name
		self.default_value = default_value.decode('utf8')
		self.regexp = ""

	def __repr__(self):
		return "VDOM type attribute (name='%s')" % self.name

	def __str__(self):
		return repr(self)
