"""application structure module"""

class VDOM_structure_item:
	"""this class represents one container in the application structure"""

	def __init__(self, ident):
		"""constructor"""
		self.id = ident
		self.index = 0
		self.children = []
		self.parents = []

class VDOM_structure_level:
	"""this class represents application structure level"""

	def __init__(self, lnum):
		"""constructor"""
		self.level_number = lnum
		self.level_map = {}	# hash of all objects on this level

	def set_item(self, obj):
		"""add VDOM_structure_item object to the level"""
		self.level_map[obj.id] = obj
