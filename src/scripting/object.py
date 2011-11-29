
import sys, re

from wrappers import obsolete_request # from . import request
from e2vdom import global_context
from utils.exception import *

from actions import *

import managers

#rexp2 = re.compile(r"\#lang\(([0-9]+)\)", re.IGNORECASE)

attribute_value_name="%s_value"

stage_initialize="initialize"
stage_normal="normal"
stage_deinitialize="deinitialize"
stage_action="action"

compute_require_recompute="require recompute"
compute_recompute_in_progress="recompute in progress"
compute_up_to_date="up to date"

state_up_to_date="up to date"
state_require_update="update"

class VDOM_descriptor(object):

	def __init__(self, name):
		self.__name=name

	def __get__(self, master, type=None):
		if master.stage is stage_normal or master.stage is stage_action:
			# debug("[Descriptor] Get %s attribute '%s'"%(master.id, self.__name))
			if master.compute_state is compute_require_recompute:
				master.recompute()
			return getattr(master, attribute_value_name%self.__name)
		else:
			raise AttributeError

	def __set__(self, master, value):
		if master.stage is stage_normal:
			# debug("[Descriptor] Set %s attribute '%s', value %s"%(master.id, self.__name, repr(value)))
			master.update_state=state_require_update
			if master.compute_state is compute_up_to_date:
				master.compute_state=compute_require_recompute
			setattr(master, attribute_value_name%self.__name, value)
		else:
			raise AttributeError

	def __delete__(self, master):
		raise AttributeError

class VDOM_object(object):

	def __init__(self, id):
		debug("[Object] Initialize %s"%id)
		self.__id=id
		self.__object=obsolete_request.vdom.search_object(id)
		self.__type=self.__object.type
		self.stage=stage_initialize
		self.compute_state=compute_require_recompute
		self.__attributes=[]
		self.__objects={}
		temp = None
		for attribute in self.__object.get_attributes().values():
			# debug("[Object] Load %s attribute '%s', value %s"%(self.__id, attribute.name, repr(attribute.value)))
			if not attribute.name in type(self).__dict__:
				setattr(type(self), attribute.name, VDOM_descriptor(attribute.name))

			attribute_value = attribute.value
			if attribute.value.count("#Lang") != 0:
				temp = self.test4lang(attribute.value)
				if obsolete_request.session["vdom_current_language"] not in self.__object.languages:
					for i in xrange(attribute.value.count("#Lang")):
						if temp[i] in self.__object.languages[managers.request_manager.get_request().application().default_language]:
							attribute_value = attribute.value.replace('#Lang('+temp[i]+')',self.__object.languages[managers.request_manager.get_request().application().default_language][temp[i]])	
				else:
					for i in xrange(attribute.value.count("#Lang")):
						if temp[i] in self.__object.languages[obsolete_request.session["vdom_current_language"]]:
							attribute_value = attribute.value.replace('#Lang('+temp[i]+')',self.__object.languages[obsolete_request.session["vdom_current_language"]][temp[i]])			


			setattr(self, attribute_value_name%attribute.name, attribute_value)
			self.attributes.append(attribute.name)
		self.order=type(self.__object).__dict__.get("order", 0)
		# - - - little cheat for table objects  - - - - - - - - - - - - - - - - - - - #
		if "top" in type(self).__dict__ and "left" in type(self).__dict__:
			self.position="absolute"
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
		self.update_state=state_up_to_date
		self.stage=stage_normal

#	def __del__(self): WARNING: Temporary removed due memory leaks
#		debug("[Object] Deinitialize %s"%self.__id)
#		self.stage=stage_deinitialize
#		self.__object=None
#		self.__attributes=None
#		self.__objects=None

	def __get_name(self):
		return self.__object.name

	def	__set_name(self, value):
		raise AttributeError

	name=property(__get_name, __set_name)

	def __get_class_name(self):
		return self.__class__.__name__

	def	__set_class_name(self, value):
		raise AttributeError

	class_name=property(__get_class_name, __set_class_name)

	def __get_original_class_name(self):
		return self.__object.type.class_name

	def	__set_original_class_name(self, value):
		raise AttributeError

	original_class_name=property(__get_original_class_name, __set_original_class_name)

	def __get_id(self):
		return self.__id

	def	__set_id(self, value):
		raise AttributeError

	id=property(__get_id, __set_id)

	def __get_id_special(self):
		return "o_%s"%self.__id.replace('-', '_')

	def	__set_id_special(self, value):
		raise AttributeError

	id_special=property(__get_id_special, __set_id_special)

	def __get_object(self):
		return self.__object

	def	__set_object(self, value):
		raise AttributeError

	object=property(__get_object, __set_object)

	def __get_attributes(self):
		return self.__attributes

	def	__set_attributes(self, value):
		raise AttributeError

	attributes=property(__get_attributes, __set_attributes)

	def __get_objects(self):
		return self.__objects

	def	__set_objects(self, value):
		raise AttributeError

	objects=property(__get_objects, __set_objects)

	def __get_type(self):
		return self.__type

	def __set_type(self, value):
		raise AttributeError

	type=property(__get_type, __set_type)

	def execute(self, action_name, context):
		# debug("[Object] Execute context %s, self.__id %s"%(context, self.__id))
		if context is global_context or self.__id==context:
			action=self.__object.actions["name"].get(action_name, None)
			if action and action.code:
				debug("[Object] Execute %s action \"%s\" in context %s:"%(self.__id, action_name, context))
				if action.cache is None:
					language=managers.request_manager.get_request().application().scripting_language
					#if action.lang=="python":
					if language=="python":
						action.cache=python_action(self, action_name, action.code)
					#elif action.lang=="vscript":
					elif language=="vscript":
						action.cache=vscript_action(self, action_name, action.code)
					else:
						raise VDOM_exception("Unknown action language")
				action.cache.execute(self, managers.request_manager.get_request().session().context)
		else:
			#debug("[Object] HAS NO SCRIPT!!!")
			pass

	def update(self, *arguments):
		for argument in arguments:
			name=unicode(argument).lower()
			value=getattr(self, attribute_value_name%name)
			# debug("[Object] Save %s attribute '%s', value %s"%(self.__id, name, repr(value)))
			self.__object.set_attribute_ex(name, value)

	def compute(self):
		debug("[Object] Compute %s"%self.__id)

	def recompute(self):
		self.compute_state=compute_recompute_in_progress
		self.compute()
		self.compute_state=compute_up_to_date

	def render(self, parent, contents=""):
		debug("[Object] Render %s"%self.__id)
		return contents

	def render_separate(self, parent):
		debug("[Object] Render separate %s"%self.__id)
		if self.update_state is state_require_update:
			return {self.__id: self.render(parent)}
		else:
			result={}
			for object in self.__objects.itervalues():
				result.update(object.render_separate(self.__id))
			return result

	def wysiwyg(self, parent, contents=""):
		debug("[Object] Wysiwyg %s contents:\n- - - - - - - - - - - - - - - - - - - -\n%s\n- - - - - - - - - - - - - - - - - - - -"%(self.__id, contents))
		return contents

	def write(self, data):
		debug("[Object] Write data to client %s"%data)
		self.stage=stage_action
		obsolete_request.add_client_action(self.__id, data)

	def action(self, action_name, param = [], source_id = None):
		"""Client action call from server action"""

		if source_id:
			src_id = "SRC_ID=\"o_%s\" "% source_id.replace('-', '_')
		else:
			src_id = ""
		#self.write ("<EXECUTE %sDST_ID=\"%s\" ACT_NAME=\"%s\"><PARAM><![CDATA[%s]]></PARAM></EXECUTE>\n"%(src_id,self.__id.replace('-', '_'),action_name, param))

		if type(param) != list:
			param = [param]

		params = ""
		import types
		import json
		for val in param:
			if isinstance(val, types.StringTypes):
				xtype = 'str'
				xval = unicode(val) # NO str() !!! unicode() ONLY
			else:
				xtype = 'obj'
				xval = unicode(json.dumps(val))
			params += "<PARAM type=\"%s\"><![CDATA[%s]]></PARAM>" % ( xtype, xval )

		self.write("<EXECUTE %sDST_ID=\"%s\" ACT_NAME=\"%s\">%s</EXECUTE>" % (src_id, self.__id.replace('-', '_'), action_name, params))

	def test4lang(self, value):
		"""test for #Lang(N)"""
		ret = []
		ret1 = None
		ret2 = None
		tempvalue=value
		for i in xrange(value.count("#Lang")):
			ret1 = tempvalue.find("#Lang(") + 6
			ret2 = tempvalue[ret1:].find(")")
			ret.append(tempvalue[ret1:ret1+ret2])
			tempvalue=tempvalue[ret1+ret2+1:]
		return ret

