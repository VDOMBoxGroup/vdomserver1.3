
import sys, thread, time, traceback

import utils.exception
import utils.id
import managers

from sandbox import VDOM_sandbox
from e2vdom import global_context, action_render, action_wysiwyg
from vscript.engine import vcompile, vexecute
import scripting # from object import request

#import profile

from exceptions import RenderTermination
from utils.exception import VDOM_timeout_exception


class VDOM_engine:
	""" Engine class """

	def compute(self, application, object, parent):
		""" Compute container """
		debug("[Engine] Compute %s (application %s)"%(object.id, application.id))
		#application.lock()
		try:
			source=managers.source_cache.get_source(application, object, action_render, global_context)
			result=source.compute(parent.id if parent else "")
			managers.request_manager.get_request().application().sync()
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

			source=managers.source_cache.get_source(application, object, action_render, global_context)
			try:
				result=source.render(parent.id if parent else "")
			except VDOM_timeout_exception:
				if application.global_actions["request"]["request"+"ontimeout"].code:
					self.special(application, application.global_actions["request"]["requestontimeout"])
				raise			
			except RenderTermination:
				result=""

#			profile.runctx('result=managers.source_cache.get_source(application, object, action_render, global_context).render(parent.id if parent else "")', myglobals, mylocals)
#			result=mylocals["result"]

			managers.request_manager.get_request().application().sync()
			return result
		except Exception as error:
			traceback.print_exc()
			raise
		finally:
			pass
			#application.unlock()

	def wysiwyg(self, application, object, parent, dynamic):
		""" Render wysiwyg representaiont of the object """
		debug("[Engine] Wysiwyg %s (application %s)"%(object.id, application.id))
		#application.lock()
		try:
			source=managers.source_cache.get_source(application, object, action_wysiwyg, global_context)
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
			source=managers.source_cache.get_source(application, object, action_name, object.id)
			try:
				result=source.execute(parent.id if parent else "", silent)
			except RenderTermination:
				result=""
			managers.request_manager.get_request().application().sync()
			return result
		finally:
			pass
			#application.unlock()

	def special(self, application, action, namespace=None):
		""" Execute special action """
		debug("[Engine] Execute special action \"%s\" (application %s)"%(action.name, application.id))
		#application.lock()
		try:
			scripting.application.set_app_id(application.id)
			if action and action.code:
				language=application.scripting_language
				#if action.lang=="python":
				if language=="python":
					#debug("- - - - - - - - - - - - - - - - - - - -\n%s\n- - - - - - - - - - - - - - - - - - - -"%action.code)
					# namespace={"request": request, "self": None, "__package__": application.id }
					namespace={"server": scripting.server, "application": scripting.application, "log": scripting.log, 
						"session": scripting.session, "request": scripting.request, "response": scripting.response,
						"obsolete_request": scripting.obsolete_request, 
						"self": None, "__package__": application.id}
					exec action.code in namespace
				#elif action.lang=="vscript":
				elif language=="vscript":
					code, vsource=vcompile(action.code, package=application.id)
					if namespace is None:
						namespace=managers.request_manager.get_request().session().context
					vexecute(code, vsource, namespace=namespace)
		finally:
			pass
			#application.unlock()

	def terminate(self):
		debug("[Engine] Terminate render")
		raise RenderTermination


from source.source import VDOM_source
