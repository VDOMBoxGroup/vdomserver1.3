"""e2vdom info module"""

class VDOM_event_info():
	"""event info class"""

	def __init__(self):
		self.support_event = False
		self.event_processing_engine = ""	# source code
		self.engine_classes = []	# list of pairs (function, name)
		self.user_interface_events = []	# list of names
		self.object_events = {}	# map name:[VDOM_parameter(), ...]


class VDOM_action_info():
	"""action info class"""

	def __init__(self):
		self.id = ""
		self.method_name = ""
		self.parameters = []	# list of VDOM_parameter()
		self.source_code = ""
		self.target_object = ""
		self.xml_obj = None
		self.top = ""
		self.left = ""
		self.state = ""

	def __repr__(self):
		return "VDOM action info (method_name='%s' id='%s' target_object='%s')" % (self.method_name, self.id, self.target_object)

	def __str__(self):
		return repr(self)


class VDOM_parameter():

	def __init__(self):
		self.name = ""
		self.default_value = ""
		self.order = ""
		self.vbtype = ""
		self.value = ""

	def __repr__(self):
		return "VDOM parameter (name='%s')" % self.name

	def __str__(self):
		return repr(self)


class VDOM_application_event():
	"""application event info class"""

	def __init__(self):
		self.name = ""
		self.source_object = ""
		self.container = ""
		self.actions = []	# list of actions IDs
		self.xml_obj = None
		self.top = ""
		self.left = ""
		self.state = ""

	def __repr__(self):
		return "VDOM application event (name='%s' source_object='%s')" % (self.name, self.source_object)

	def __str__(self):
		return repr(self)


class VDOM_server_action():
	"""server action class"""

	def __init__(self, _code, _id, _top, _left, _state, _name):
		self.id = _id
		self.name = _name
		self.code = _code
		self.top = _top
		self.left = _left
		self.state = _state
		self.xml_obj = None
		self.cache = None

	def __repr__(self):
		return "VDOM server action (name='%s' id='%s')" % (self.name, self.id)

	def __str__(self):
		return repr(self)


class VDOM_client_server_events:

	def __init__(self, data):
		"""constructor, parse event data"""
		self.sid = None
		self.appid = None
		self.events = {}
		try:
			root = xml_object(srcdata=data)#.encode("utf-8"))
			if root.lname != "events":
				raise VDOM_exception_element(root.lname)
			session_id = root.get_child_by_name("session").attributes["id"]
			if not session_id:
				raise VDOM_exception_element("session")
			self.sid = session_id
			app_id = root.get_child_by_name("application").attributes["id"]
			if not app_id:
				raise VDOM_exception_element("application")
			self.appid = app_id
			for child in root.children:
				if child.lname == "event":
					source_obj_id = child.attributes["objsrcid"]
					source_obj_id = "-".join(source_obj_id[2:].split("_"))
					event_name = child.attributes["name"]
					if not source_obj_id or not event_name:
						continue
					params = {}
					for child2 in child.children:
						if child2.lname == "parameter":
							param_name = child2.attributes["name"]
							if not param_name:
								raise VDOM_exception_element("parameter")
							params[param_name] = [child2.value]
					self.events[(source_obj_id, event_name)] = params
		except VDOM_exception:
			raise
		except Exception, e:
			debug("Event exception: " + str(e))

from src.xml.xml_object import xml_object
from src.util.exception import *
