"""
User class module
"""

class VDOM_user:
	"""User class defines behaviour of account"""

	def __init__(self):
		self.id = ""
		self.login = ""
		self.password = ""
		self.first_name = ""
		self.last_name = ""
		self.email = ""
		self.security_level = ""
		self.member_of = []	# list of group names
		self.system = False
