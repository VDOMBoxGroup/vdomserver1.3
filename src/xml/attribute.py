"""XML attribute module"""

class VDOM_attribute:
	"""XML attribute class"""

	def __init__(self, name, value, xml_obj):
		"""constructor"""
		self.name = name
		self.value = value
		self.original_value = value
		self.xml_obj = xml_obj

	def __repr__(self):
		return "VDOM attribute (name='%s')" % self.name

	def __str__(self):
		return repr(self)
