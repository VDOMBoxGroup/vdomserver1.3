"""base module"""

class VDOM_module:
	"""base module class"""

	def __init__(self):
		"""constructor"""
		pass

	def __del__(self):
		"""destructor"""
		pass

	def run(self, request_object):
		"""process request"""
		pass	# implement in derivatives


class VDOM_module_post(VDOM_module):
	"""base post processing module"""

	def run(self, data):
		"""process and return modified data"""
		# no processing here
		return data
