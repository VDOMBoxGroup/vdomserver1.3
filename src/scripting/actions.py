
import thread, threading

import managers
import packages

import scripting # from object import request
from vscript.engine import vcompile, vexecute



class generic_action(object):

	def __init__(self, id, name, source):
		self.id=id
		self.name=name
		self.source=source
		self.code=None

	def compile(self):
		debug("[Action] Compile %s action \"%s\":"%(self.id, self.name))

	def on_execute(self, object, namespace):
		pass

	def execute(self, object, namespace=None):
		application=managers.request_manager.get_request().application()
		threading.currentThread().application=application.id
		if self.code is None:
			self.compile()
		self.on_execute(object, namespace)
		threading.currentThread().application=None

class python_action(generic_action):

	def compile(self):
		generic_action.compile(self)
		#debug("- - - - - - - - - - - - - - - - - - - -\n%s\n- - - - - - - - - - - - - - - - - - - -"%self.source)
		self.code=compile(self.source, "action: %s:%s"%(self.id, self.name), u"exec")

	def on_execute(self, object, namespace):
		app_module=managers.request_manager.get_request().application().id
		__import__(app_module)
		namespace={"server": scripting.server, "application": scripting.application, "log": scripting.log, 
			"session": scripting.session, "request": scripting.request, "response": scripting.response,
			"obsolete_request": scripting.obsolete_request, 
			"self": object, "__package__": app_module, "packages": packages}
		exec self.code in namespace
		
class vscript_action(generic_action):

	def __init(self, object, name, source):
		action.__init__(self, object, name, source)
		self.vsource=None

	def compile(self):
		app_module=managers.request_manager.get_request().application().id
		generic_action.compile(self)
		self.code, self.vsource=vcompile(self.source, package=app_module)

	def on_execute(self, object, namespace):
		vexecute(self.code, self.vsource, object, namespace)
