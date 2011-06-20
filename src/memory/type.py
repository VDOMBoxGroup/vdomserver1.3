"""XML type module"""

import sys, re, string

from parser import VDOM_parser

if_re = re.compile(r"^([^\(]+)\((.*?)\)$", re.IGNORECASE)

class VDOM_type(VDOM_parser):
	"""XML VDOM type class"""

	def __init__(self):
		"""constructor"""
		self.parse_list = ["information", "attributes", "sourcecode", "resources", "e2vdom", "libraries"]
		self.info_map = {
			"id":			["id", "str(%s).lower()"],
			"name":			["name", "%s"],
			"displayname":		["display_name", "%s"],
			"dynamic":		["dynamic", "int(%s)"],
			"moveable":		["moveable", "int(%s)"],
			"resizable":		["resizable", "int(%s)"],
			"optimizationpriority":	["optimization_priority", "int(%s)"],
			"classname":		["class_name", "%s"],
			"container":		["container", "int(%s)"],
			"containers":		["containers", """map(string.strip, %s.split(","))"""],
			"rendertype":		["render_type", "%s"],
			"httpcontenttype":	["http_content_type", "%s"],
			"version":		["version", "%s"],
			"remotemethods":	["remote_methods", """map(string.strip, %s.split(","))"""],
			"handlers":		["handlers", """map(string.strip, %s.split(","))"""]
		}
		self.attribute_map = {
			"name":			"name",
			"defaultvalue":		"default_value",
			"codeinterface":	"code_interface",
			"regularexpressionvalidation":	"regexp"
		}
		# type attributes
		self.attributes = {}
		self.interfaces = {}
		self.resources = {}
		self.containers = []
		# libraries
		self.lib = {}
		# libraries as temporary resources
		self.extlib = {}
		# event stuff
		self.event_info = VDOM_event_info()
		self.action_info = {} # map container_id : {method_name: VDOM_action_info(), ...}
		# required attributes
		self.required_attributes = ["id", "name"]
		# base
		VDOM_parser.__init__(self)

	def create(self, xml_obj):
		had_resources = xml_obj.get_child_by_name("Resources") is not None
		# base
		VDOM_parser.create(self, xml_obj)
		# save xml to file
		self.filename = "%s/%s.xml"%(VDOM_CONFIG["TYPES-LOCATION"],self.name)
		if had_resources:
			xml_obj.sync(self.filename)
		if hasattr(self, "remote_methods"):
			for func_name in self.remote_methods:
				managers.dispatcher.add_remote_method(self.id, func_name)
		if hasattr(self, "handlers"):
			for func_name in self.handlers:
				managers.dispatcher.add_handler(self.id, func_name)
		xml_obj.delete()

	def __repr__(self):
		return "VDOM type (name='%s' id='%s')" % (self.name, self.id)

	def __str__(self):
		return repr(self)

	def get_xml_as_string(self):
		"""get xml document as string"""
		f = open(self.filename, "rb")
		data = f.read()
		f.close()
		return data.decode("utf-8")

	def get_attributes(self):
		"""get type attributes"""
		return self.attributes

	def parse_resources(self, xml_obj):
		if xml_obj.children:
			managers.resource_manager.invalidate_resources(self.id)
		VDOM_parser.parse_resources(self, xml_obj)

	def parse_sourcecode(self, xml_obj):
		"""parse source code section"""
		src2 = xml_obj.value
		# append import section
		# TODO: Join all import from scripting code
		#src2 = "from object.request import VDOM_request\n\nrequest = VDOM_request()\n\nfrom object.object import VDOM_object\n\n%s\n" % src2.strip()
		src2="from scripting import server, application, session, request, response, VDOM_object, obsolete\n\n%s\n" % src2.strip()
		# write source code to the file
		managers.source_cache.store_type(self.id, src2)

	def save_resource(self, res_id, res_format, res_name, data):
		"""method to save resource"""
		attributes = {
			"id" : res_id,
			"name" : res_name,
			"res_format": res_format,
			}
		managers.resource_manager.add_resource(self.id, None, attributes, data)
 
	def parse_attributes(self, xml_obj):
		"""parse type attributes"""
		for child in xml_obj.children:
			self.parse_attribute(child)

	def parse_attribute(self, xml_obj):
		"""parse one type attribute"""
		regexp = ""
		for child in xml_obj.children:
			if child.lname in self.attribute_map:
				exec self.attribute_map[child.lname] + "= \"\"\"" + child.value + "\"\"\""
		self.attributes[name] = VDOM_type_attribute(name, default_value)
		self.attributes[name].regexp = regexp
		try:
			code_interface = code_interface.lower().strip()
			ret = if_re.search(code_interface)
			if ret:
				code_name = ret.groups()[0].strip()
				code_param = ret.groups()[1].strip()
				if code_name not in self.interfaces:
					self.interfaces[code_name] = map(string.strip, code_param.split(","))
		except:
			raise

	def parse_e2vdom(self, xml_obj):
		"""parse events section"""
		for child in xml_obj.children:
			getattr(self, "parse_e2vdom_" + child.lname)(child)

	def parse_e2vdom_events(self, xml_obj):
		for child in xml_obj.children:
			getattr(self, "parse_e2vdom_events_" + child.lname)(child)

	def parse_e2vdom_events_container(self, xml_obj):
		if "1" == xml_obj.attributes["eventssupported"]:
			self.event_info.support_event = True
			el = xml_obj.get_child_by_name("eventprocessingengine")
			if el and "1" == el.attributes["self"]:
				self.event_info.event_processing_engine = el.value
			el = xml_obj.get_child_by_name("engineclass")
			if el:
				for child in el.children:
					if "class" == child.lname:
						f = child.attributes["function"]
						n = child.attributes["name"]
						if f and n:
							self.event_info.engine_classes.append((f, n))

	def parse_e2vdom_events_userinterfaceevents(self, xml_obj):
		for child in xml_obj.children:
			if "event" == child.lname:
				n = child.attributes["name"]
				if n:
					self.event_info.user_interface_events.append(n)

	def parse_e2vdom_events_objectevents(self, xml_obj):
		for child in xml_obj.children:
			if "event" == child.lname:
				n = child.attributes["name"]
				if not n:
					continue
				self.event_info.object_events[n] = []
				el = child.get_child_by_name("parameters")
				if el:
					for p in el.children:
						if "parameter" == p.lname:
							par = VDOM_parameter()
							par.name = p.attributes["name"]
							par.vbtype = p.attributes["vbtype"]
							par.order = p.attributes["order"]
							self.event_info.object_events[n].append(par)

	def parse_e2vdom_actions(self, xml_obj):
		for child in xml_obj.children:
			if "container" == child.lname:
				self.parse_e2vdom_actions_container(child)

	def parse_e2vdom_actions_container(self, xml_obj):
		id_cont = xml_obj.attributes["id"]
		if not id_cont:
			return
		self.action_info[id_cont] = {}
		for act in xml_obj.children:
			if "action" == act.lname:
				a = VDOM_action_info()
				a.method_name = act.attributes["methodname"]
				if not a.method_name:
					continue
				self.action_info[id_cont][a.method_name] = a
				par = act.get_child_by_name("parameters")
				if par:
					for p in par.children:
						if "parameter" == p.lname:
							par = VDOM_parameter()
							par.name = p.attributes["scriptname"]
							par.default_value = p.attributes["defaultvalue"]
							a.parameters.append(par)
				src2 = act.get_child_by_name("sourcecode")
				if src2:
					a.source_code = src2.value.strip()

	def parse_libraries(self, xml_obj):
		"""parse type libraries"""
		for child in xml_obj.children:
			if "library" == child.lname:
				target = child.attributes["target"].lower()
				if target:
					if target not in self.lib:
						self.lib[target] = []
					self.lib[target].append(child.value)
			elif "extlibrary" == child.lname:
				target = child.attributes["target"].lower()
				if target:
					if target not in self.lib:
						self.extlib[target] = []
					self.extlib[target].append(child.value)
			

import managers
import utils.id
from utils.exception import *
from type_attribute import VDOM_type_attribute
from event import *
