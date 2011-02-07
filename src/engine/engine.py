"""
Engine
"""

import sys
import thread
import time

import src.util.exception
import src.util.id
import src.xml

from src.engine.sandbox import VDOM_sandbox
from src.e2vdom import global_context, action_render, action_wysiwyg
from src.vscript.engine import vcompile, vexecute
from src.object import request

import src.request
#import profile

from exceptions import RenderTermination



class VDOM_engine:
	""" Engine class """

	def compute(self, application, object, parent):
		""" Compute container """
		debug("[Engine] Compute %s (application %s)"%(object.id, application.id))
		#application.lock()
		try:
			source=src.source.cache.get_source(application, object, action_render, global_context)
			result=source.compute(parent.id if parent else "")
			src.request.request_manager.get_request().application().sync()
			return result
		finally:
			pass
			#application.unlock()

	def render(self, application, object, parent, render_type):
		""" Render container """
		debug("[Engine] Render %s (application %s)"%(object.id, application.id))
		#application.lock()
		try:
			myglobals, mylocals=globals(), locals()

			source=src.source.cache.get_source(application, object, action_render, global_context)
			try:
				result=source.render(parent.id if parent else "")
			except RenderTermination:
				result=""

#			profile.runctx('result=src.source.cache.get_source(application, object, action_render, global_context).render(parent.id if parent else "")', myglobals, mylocals)
#			result=mylocals["result"]

			src.request.request_manager.get_request().application().sync()
			return result
		finally:
			pass
			#application.unlock()

	def wysiwyg(self, application, object, parent, dynamic):
		""" Render wysiwyg representaiont of the object """
		debug("[Engine] Wysiwyg %s (application %s)"%(object.id, application.id))
		#application.lock()
		try:
			source=src.source.cache.get_source(application, object, action_wysiwyg, global_context)
			result=source.wysiwyg(parent.id if parent else "")
			return result
		finally:
			pass
			#application.unlock()
		
	def execute(self, application, object, parent, action_name, silent=None):
		""" Execute specific action """
		debug("[Engine] Execute %s action \"%s\" (application %s)"%(object.id, action_name, application.id))
		#application.lock()
		try:
			source=src.source.cache.get_source(application, object, action_name, object.id)
			try:
				result=source.execute(parent.id if parent else "", silent)
			except RenderTermination:
				result=""
			src.request.request_manager.get_request().application().sync()
			return result
		finally:
			pass
			#application.unlock()

	def special(self, application, action, namespace=None):
		""" Execute special action """
		debug("[Engine] Execute special action \"%s\" (application %s)"%(action.name, application.id))
		#application.lock()
		try:
			if action and action.code:
				language=application.scripting_language
				#if action.lang=="python":
				if language=="python":
					debug("- - - - - - - - - - - - - - - - - - - -\n%s\n- - - - - - - - - - - - - - - - - - - -"%action.code)
					namespace={"request": request, "self": None, "__package__": application.id }
					exec action.code in namespace
				#elif action.lang=="vscript":
				elif language=="vscript":
					code, vsource=vcompile(action.code, package=application.id)
					if namespace is None:
						namespace=src.request.request_manager.get_request().session().context
					vexecute(code, vsource, namespace=namespace)
		finally:
			pass
			#application.unlock()

	def terminate(self):
		debug("[Engine] Terminate render")
		raise RenderTermination



internal_engine=VDOM_engine()
del VDOM_engine

from src.source.source import VDOM_source
