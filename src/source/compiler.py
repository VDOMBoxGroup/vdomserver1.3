""" Compiler """

import sys
import re

import utils.exception
import utils.id
import managers

from source import VDOM_source
from e2vdom import global_context, virtual_context

import auxilary


class VDOM_compiler(object):
	""" Compiler class """

	__modules={}
	__search_self_pattern=re.compile("self\.(?P<name>[_A-Za-z][_0-9A-Za-z]*)")

	def compile(self, application, object, action_name, context):
		""" Compile objects """
		#debug("[Compiler] Compile %s action \"%s\" in context %s (application %s)"%(object.id, action_name, context, application.id))

		attributes=object.get_attributes()
		objects=[]; status=[]

		if not hasattr(object, "dynamic"):
			object.dynamic={(action_name, context): object.type.dynamic}
		else:
			object.dynamic.setdefault((action_name, context), object.type.dynamic)
		if context==virtual_context: object.dynamic=1

		if not hasattr(object, "optimization_priority"):
			object.optimization_priority=object.type.optimization_priority
		
		object.types={object.type.id: object.type}
		object.containers={}
		object.libraries={}

		action=object.actions["name"].get(action_name, None)
		if action and action.code and (context is global_context or object.id==context):
			#debug("[Compiler] Assume %s as dynamic, contain action \"%s\" in context %s"%(object.id, action_name, context))
			if context!=virtual_context: object.dynamic[(action_name, context)]=1
			# WARNING: Leonid reports to application may not have scripting_language attribute...
			try: scripting_language=application.scripting_language
			except: scripting_language="python"
			names=auxilary.analyse_script_structure(action.code, scripting_language)
			auxilary.enable_dynamic(object, action_name, context, names)

		module_name=utils.id.guid2mod(object.type.id)
		print module_name
		if module_name in self.__modules:
			module=self.__modules[module_name]
		else:
			#debug("[Compiler] Object %s, import module %s"%(object.id, module_name))
			try:
				module=__import__(module_name)
			except Exception as e:
				print e
				raise
			self.__modules[module_name]=module
		if "on_compile" in module.__dict__:
			#debug("[Compiler] Call \"on_compile\" handler")
			status.append("on_compile")
			objects=module.on_compile(application, object, action_name, context, objects)

		contain_objects=len(objects)
		if contain_objects:
			if contain_objects>1:
				status.append("%d objects"%contain_objects)
			else:
				status.append("1 object")

		if objects:
			order=0
			for item in objects:
				xobject=item["object"]
				xobject.order=order
				#debug("[Compiler] Object %s, order %s"%(xobject.id, xobject.order))
				order+=1

		#if status:
		#	debug("[Compiler] Object %s, type %s (%s)"%(object.id, object.type.class_name, ", ".join(status)))
		#else:
		#	debug("[Compiler] Object %s, type %s"%(object.id, object.type.class_name))

		if "html" in object.type.lib:
			object.libraries[object.type.id]=object.type.lib["html"]
		
		if object.type.container in (2, 3):
			object.containers[object.type.id]=object.type			

		if contain_objects:
		
			source=VDOM_source(object.name, "container_"+"_".join(object.id.split("-")), object.id, action_name, context)
			source.import_module(module_name, object.type.class_name)
			
			dynamic=object.dynamic[(action_name, context)]; maximum_priority=0; maximum_hierarchy=0
			for item in objects:
				xobject=item["object"]
				#debug("[Compiler] Enumerate %s object"%xobject.id)
				if xobject.type.optimization_priority>maximum_priority:
					maximum_priority=xobject.type.optimization_priority
				if int(xobject.attributes["hierarchy"].value)>maximum_hierarchy:
					maximum_hierarchy=int(xobject.attributes["hierarchy"].value)
				"""
				managers.source_cache.get_source(application, xobject, action_name, context)
				if xobject.dynamic[(action_name, context)]: object.dynamic[(action_name, context)]=1
				object.types.update(xobject.types)
				object.containers.update(xobject.containers)
				object.libraries.update(xobject.libraries)
				"""

			#if dynamic!=object.dynamic[(action_name, context)]:
			#	debug("[Copy] Assume %s as dynamic in action %s:%s, contains dynamic object"%(object.id, action_name, context))
			
			xobjects, xghosts=[], []; init=dein=execute=compute=render=wysiwyg=""
			for hierarchy in range(maximum_hierarchy+1):
				for priority in range(maximum_priority+1):
					for item in objects:
						xobject=item["object"]

						option_name=item.get("name", None)
						realname=option_name or xobject.name

						option_init=item.get("init", None)
						option_execute=item.get("execute", None)
						option_compute=item.get("compute", None)
						option_render=item.get("render", None)
						option_wysiwyg=item.get("wysiwyg", None)

						if hierarchy==int(xobject.attributes["hierarchy"].value) and priority==xobject.type.optimization_priority:
							#if xobject.dynamic[(action_name, context)]:
							#	debug("[Compiler] Include %s as dynamic"%xobject.id)
							#else:
							#	debug("[Compiler] Include %s as static"%xobject.id)

							xattributes=xobject.get_attributes()
							if option_name:
								xsource=managers.compiler.compile(application, xobject, action_name, context)
							else:
								xsource=managers.source_cache.get_source(application, xobject, action_name, context)

							object.types.update(xobject.types)
							object.containers.update(xobject.containers)
							object.libraries.update(xobject.libraries)

							if xobject.dynamic[(action_name, context)]:
								object.dynamic[(action_name, context)]=1
								source.include(xsource)
								xobjects.append(realname)
								
								init+="\t\tself.%s=%s(%s)\n\t\tself.%s.order=%s\n"%(realname,
									xsource.class_name, repr(xsource.id), realname, repr(xobject.order))
								if option_init:
									init+="".join(["\t\t%s\n"%line for line in option_init])
								dein+="\t\tdel self.%s\n"%realname
								
								if option_execute:
									execute+="".join(["\t\t%s\n"%line for line in option_execute])
								execute+="\t\tself.%s.execute(action_name, context)\n"%(realname)
								
								if option_compute:
									compute+="".join(["\t\t%s\n"%line for line in option_compute])
								
								compute+="\t\tself.%s.recompute()\n"%(realname)
								
								if option_render:
									render+="".join(["\t\t%s\n"%line for line in option_render])
								render+="\t\tresult+=self.%s.render(%s)\n"%(realname, repr(object.id))

								if option_wysiwyg:
									wysiwyg+="".join(["\t\t%s\n"%line for line in option_wysiwyg])
								wysiwyg+="\t\tresult+=self.%s.wysiwyg(%s)\n"%(realname, repr(object.id))
							else:
								xghosts.append(realname)
								if option_init or option_render:
									names={}
									if option_init:
										for line in option_init:
											for match in self.__search_self_pattern.finditer(line):
												name=match.group("name").lower()
												if name in attributes:
													names[name]=None
									if option_render:
										for line in option_render:
											for match in self.__search_self_pattern.finditer(line):
												name=match.group("name").lower()
												if name in attributes:
													names[name]=None
									render_include="".join(["%s=%s\n"%(name, repr(attributes[name].value)) for name in names])
									if option_init:
										render_include+="".join(["%s\n"%line.replace("self.", "") for line in option_init])
									if option_render:
										render_include+="".join(["%s\n"%line.replace("self.", "") for line in option_render])
								else:
									render_include=None
								render+="\t\tresult+=%s\n"%repr(xsource.render("", include=render_include))
								if option_init or option_wysiwyg:
									wysiwyg_include=""
									if option_init:
										render_include+="".join(["%s\n"%line.replace("self.", "") for line in option_init])
									if option_wysiwyg:
										wysiwyg_include+="".join(["%s\n"%line.replace("self.", "") for line in option_wysiwyg])
								else:
									wysiwyg_include=None
								wysiwyg+="\t\tresult+=%s\n"%repr(xsource.wysiwyg("", include=wysiwyg_include))

			source.write("class %s(%s):\n\n"%(source.class_name, object.type.class_name))
			source.write("\tdef __init__(self, id):\n\t\t%s.__init__(self, id)\n%s%s\n"%(object.type.class_name, init,
				"\t\tself.objects.update({%s})\n"%", ".join(["%s: self.%s"%(repr(name), name) for name in xobjects]) if xobjects else ""))
			# source.write("\tdef __del__(self):\n\t\t%s.__del__(self)\n%s\n"%(object.type.class_name, dein)) # WARNING: Temporary removed due memory leaks
			source.write("\tdef execute(self, action_name, context):\n%s\t\t%s.execute(self, action_name, context)\n\n"%(execute, object.type.class_name))
			source.write("\tdef compute(self):\n%s\t\t%s.compute(self)\n\n"%(compute, object.type.class_name))
			source.write("\tdef render(self, parent, contents=\"\"):\n\t\tresult=contents\n%s\t\treturn %s.render(self, parent, contents=result)\n\n"%(render, object.type.class_name))
			source.write("\tdef wysiwyg(self, parent, contents=\"\"):\n\t\tresult=contents\n%s\t\treturn %s.wysiwyg(self, parent, contents=result)\n"%(wysiwyg, object.type.class_name))
		else:
			source=VDOM_source(object.name, object.type.class_name, object.id, action_name, context)
			source.import_module(utils.id.guid2mod(object.type.id), object.type.class_name)

		return source
