"""
Group class module
"""

class VDOM_usergroup:
	"""Group class defines behaviour of user group"""

	def __init__(self):
		self.id = ""
		self.login = ""
		self.description = ""
		self.members = []	# list of login names
		self.member_of = []	# list of group names
		self.system = False
