
class VDOM_singleton(object):

	__instance=None

	def __init__(self):
		if VDOM_singleton.__instance:
			raise Exception("Unable to create singleton again")
		VDOM_singleton.__instance=self
