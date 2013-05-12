""" Source """

import sys
import string

import utils.exception
import utils.id
import managers


def filter_string(string):
	if len(string)>4096:
		lines=string.split



class VDOM_source(object):
	""" Source class """

	def __init__(self, name, class_name, id, action_name, context):
		""" Constructor """
		self.name=name
		self.class_name=class_name
		self.id=id
		self.action_name=action_name
		self.context=context
		self.__modules={}
		self.__sources=[]
		self.__value=""
		self.__size=0
		self.__common_code=None
		self.__compute_code=None
		self.__render_code=None
		self.__wysiwyg_code=None
		self.__execute_code=None

	def import_module(self, module, class_name):
		""" Add module """
		self.__modules[module]=class_name

	def write(self, source):
		""" Write to source code """
		self.__value+=source
		self.__size+=len(source)

	def include(self, source):
		""" Include another source """
		self.__modules.update(source.__modules)
		self.__sources+=[source]

	def __combine_modules(self):
		""" Combine import section source code """
		result=""
#		result+="import sys\nsys.path.append(\"%s\")\n"%(VDOM_CONFIG["SOURCE-MODULES-DIRECTORY"])
		result+="import sys\n"
		result+="\n"
		# result+="import src!.object\nsrc!.object.local.request=request\n"
		# result+="import managers.request_manager.get_request()\n"

		#result+="from object import request\n"
		result+="from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request\n"

		#result+="from scripting import request\n"
		# result+="from src!.object import request\n"

		result+="\n"
		for module in self.__modules:
			result+="from %s import %s\n"%(module, self.__modules[module])
		result+="\n"
		return result

	def __combine_sources(self):
		""" Combine source code from sources """
		result=""
		for source in self.__sources:
			result+=source.__combine_sources()
		if self.__value:
			result+=self.__value
			result+="\n"
		return result

	def __compile_common(self):
		""" Compile common source code """
		source=self.__combine_modules()+self.__combine_sources()
		source+="%s=%s(%s)\n"%(self.name, self.class_name, repr(self.id))
		debug("[Source] Compile %s common code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
		self.__common_code=compile(source, "common code: %s:%s"%(self.id, self.action_name), "exec")

	def __compile_compute(self):
		""" Compile compute source code """
		source="%s.recompute()\nresult=None\ndel %s\n"%(self.name, self.name)
		debug("[Source] Compile %s compute code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
		self.__compute_code=compile(source, "compute code: %s:%s"%(self.id, self.action_name), "exec")

	def __compile_render(self):
		""" Compile render source code """
		source="%s.execute(action_name, context)\nresult=%s.render(parent)\ndel %s\n"%(self.name, self.name, self.name)
		debug("[Source] Compile %s render code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
		self.__render_code=compile(source, "render code: %s:%s"%(self.id, self.action_name), "exec")

	def __compile_wysiwyg(self):
		""" Compile wysiwyg source code """
		source="result=%s.wysiwyg(parent)\ndel %s\n"%(self.name, self.name)
		debug("[Source] Compile %s wysiwyg code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
		self.__wysiwyg_code=compile(source, "wysiwyg code: %s:%s"%(self.id, self.action_name), "exec")

	def __compile_execute(self):
		""" Compile execute source code """
		source="%s.execute(action_name, context)\nresult=%s.render_separate(parent) if silent is None else None\ndel %s\n"%(self.name, self.name, self.name)
		debug("[Source] Compile %s execute code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
		self.__execute_code=compile(source, "execute code: %s:%s"%(self.id, self.action_name), "exec")

	def __execute_compute(self, arguments):
		namespace={"action_name": self.action_name, "context": self.context, "parent": arguments["parent"]}
		exec self.__common_code in namespace
		if arguments:
			override=arguments.get("override", None)
			if override:
				source=""
				for attribute in override:
					#if override[attribute]:
					#	source+="%s.override(\"%s\", %s)\n"%(self.name, attribute, repr(override[attribute]))
					if override[attribute]:
						source+="%s.%s=%s\n"%(self.name, attribute, repr(override[attribute]))
				if source:
					debug("[Source] Override %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
					code=compile(source, "compute override code: %s:%s"%(self.id, self.action_name), "exec")
					exec code in namespace
			include=arguments.get("include", None)
			if include:
				source=include
				debug("[Source] Include %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
				code=compile(source, "compute include code: %s:%s"%(self.id, self.action_name), "exec")
				exec code in namespace
		exec self.__compute_code in namespace
		return namespace["result"]

	def __execute_render(self, arguments):
		namespace={"action_name": self.action_name, "context": self.context, "parent": arguments["parent"]}
		exec self.__common_code in namespace
		if arguments:
			override=arguments.get("override", None)
			if override:
				source=""
				for attribute in override:
					if override[attribute]:
						source+="%s.override(\"%s\", %s)\n"%(self.name, attribute, repr(override[attribute]))
				if source:
					debug("[Source] Override %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
					code=compile(source, "render override code: %s:%s"%(self.id, self.action_name), "exec")
					exec code in namespace
			include=arguments.get("include", None)
			if include:
				source=include
				debug("[Source] Include %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
				code=compile(source, "render include code: %s:%s"%(self.id, self.action_name), "exec")
				exec code in namespace
		exec self.__render_code in namespace
		return namespace["result"]

	def __execute_wysiwyg(self, arguments):
		namespace={"action_name": self.action_name, "context": self.context, "parent": arguments["parent"]}
		exec self.__common_code in namespace
		if arguments:
			override=arguments.get("override", None)
			if override:
				source=""
				for attribute in override:
					if override[attribute]:
						source+="%s.%s=%s\n"%(self.name, attribute, repr(override[attribute]))
				if source:
					debug("[Source] Override %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
					code=compile(source, "wysiwyg override code: %s:%s"%(self.id, self.action_name), "exec")
					exec code in namespace
			include=arguments.get("include", None)
			if include:
				source=include
				debug("[Source] Include %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
				code=compile(source, "wysiwyg include code: %s:%s"%(self.id, self.action_name), "exec")
				exec code in namespace
		exec self.__wysiwyg_code in namespace
		return namespace["result"]

	def __execute_execute(self, arguments):
		namespace={"action_name": self.action_name, "context": self.context, "parent": arguments["parent"], "silent": arguments["silent"]}
		exec self.__common_code in namespace
		if arguments:
			override=arguments.get("override", None)
			if override:
				source=""
				for attribute in override:
					if override[attribute]:
						source+="%s.override(\"%s\", %s)\n"%(self.name, attribute, repr(override[attribute]))
				if source:
					debug("[Source] Override %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
					code=compile(source, "execute override code: %s:%s"%(self.id, self.action_name), "exec")
					exec code in namespace
			include=arguments.get("include", None)
			if include:
				source=include
				debug("[Source] Include %s code:\n- - - - - - - - - - - - - - - - - - - -\n%s- - - - - - - - - - - - - - - - - - - -"%(self.id, string.replace(source, "\t", "    ")))
				code=compile(source, "execute include code: %s:%s"%(self.id, self.action_name), "exec")
				exec code in namespace
		exec self.__execute_code in namespace
		return namespace["result"]

	def compute(self, parent, override=None, include=None):
		""" Render """
		if not self.__common_code:
			self.__compile_common()
		if not self.__compute_code:
			self.__compile_compute()
		#debug("[Source] Compute %s"%(self.id))
		sandbox=VDOM_sandbox(self.__execute_compute)
		return sandbox.execute(VDOM_CONFIG["COMPUTE-TIMEOUT"], arguments={"parent": parent, "override": override, "include": include})

	def render(self, parent, override=None, include=None):
		""" Render """
		if not self.__common_code:
			self.__compile_common()
		if not self.__render_code:
			self.__compile_render()
		#debug("[Source] Render %s"%(self.id))
		sandbox=VDOM_sandbox(self.__execute_render)
		return sandbox.execute(VDOM_CONFIG["RENDER-TIMEOUT"], arguments={"parent": parent, "override": override, "include": include})

	def wysiwyg(self, parent, override=None, include=None):
		""" Wysiwyg """
		if not self.__common_code:
			self.__compile_common()
		if not self.__wysiwyg_code:
			self.__compile_wysiwyg()
		#debug("[Source] Wysiwyg %s"%(self.id))
		sandbox=VDOM_sandbox(self.__execute_wysiwyg)
		return sandbox.execute(VDOM_CONFIG["WYSIWYG-TIMEOUT"], arguments={"parent": parent, "override": override, "include": include})

	def execute(self, parent, silent, override=None, include=None):
		""" Render """
		if not self.__common_code:
			self.__compile_common()
		if not self.__execute_code:
			self.__compile_execute()
		#debug("[Source] Execute %s action \"%s\""%(self.id, self.action_name))
		sandbox=VDOM_sandbox(self.__execute_execute)
		return sandbox.execute(VDOM_CONFIG["RENDER-TIMEOUT"], arguments={"parent": parent, "silent": silent, "override": override, "include": include})

	def size(self):
		return self.__size

from engine.sandbox import VDOM_sandbox
