"""Module Manager module"""

import sys, traceback, shutil

import managers
from utils.exception import VDOM_exception

from resource import VDOM_module_resource
from .python import VDOM_module_python
from post_processing import VDOM_post_processing


class VDOM_module_manager(object):
	"""Module Manager class"""

	def process_request(self, request_object):
		"""process request"""
		script_name = request_object.environment().environment()["SCRIPT_NAME"]
		if "127.0.0.1" != request_object.handler().client_address[0]:
			debug("Requested URL: '" + script_name + "'")
		# dirty HACK!!!
		if script_name.lower().startswith("/images/"):
			e = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "png": "image/png", "js": "text/javascript"}
			file = open("../images/" + script_name.split("/")[-1], "rb")
			ext = script_name.split(".")[-1].lower()
			data = file.read()
			file.close()
			if ext in e:
				request_object.add_header("Content-Type", e[ext])
				request_object.add_header("Cache-Control", "max-age=86400")
			else:
				raise AttributeError, ext
			request_object.add_header("Content-Length", str(len(data)))
			return (None, data)
		elif "/favicon.ico" == script_name:
			app = request_object.application()
			if not app or not app.icon:
				return (404, None)
			try:
				request_object.environment().environment()["REQUEST_URI"] = "/%s.res" % app.icon
				module = VDOM_module_resource()
				return (None, module.run(request_object, "res"))
			except Exception, e:
				debug(_("Module manager: resource module error: %s") % str(e))
				return (404, None)

		parts1 = script_name.split("/")
		parts = parts1[-1]
		parts = parts.split(".")
		if len(parts) == 1 and parts[0] != "":
			parts.append("vdom")
		request_type = parts[-1].lower()
		request_object.request_type = request_type
		if "127.0.0.1" != request_object.handler().client_address[0]:
			debug("Request type: " + request_type)

		parts1 = filter(lambda x: "" != x, parts1)
		if 2 == len(parts1):
			try:	# preview
				a1 = managers.xml_manager.get_application(parts1[0])
				request_object.set_application_id(a1.id)
				o1 = a1.search_object(parts1[1])
				if o1 and 3 == o1.type.container:
					request_object.container_id = o1.id
					request_object.request_type = "vdom"
					result = managers.engine.render(a1, o1, None, o1.type.render_type.lower())
					return (None, result.encode("utf-8"))
			except: raise

		# check if container is present
		app = request_object.application()
		if app and len(parts) < 2:
			# have no container id, try to redirect to the top level container
			if app.index_page:
				_o = app.search_object(app.index_page)
				if _o:
					request_object.redirect("/%s.vdom" % _o.name)
				else:
					return (404, None)
			elif len(app.get_objects_list()) > 0:	# redirect to the first container
				request_object.redirect("/%s.vdom" % app.get_objects_list()[0].name)
			return (404, None)	# empty request

		# this acts as Communication Dispatcher
		if "vdom" == request_type:	# VDOM container request
			# first chek if application is OK
			if not request_object.app_id():	# application not registered
				ret = "No application registered with virtual host '%s'" % request_object.app_vhname
				debug(ret)
				return (None, ret)
			if not app:
				ret = "Application not found"
				debug(ret)
				return (None, ret)
			if "1" != app.active:	# application not active
				ret = "Application not active"
				debug(ret)
				return (None, ret)

			container_id = parts[-2].lower()
			#request_object.container_id = container_id
			#debug("Container id: " + container_id)

			# get container object and check if it can be a top level container
			_a = managers.xml_manager.get_application(request_object.app_id())
			obj = _a.search_object(container_id)
			if not obj:
				for _i in _a.objects:
					if _a.objects[_i].name == container_id:
						obj = _a.objects[_i]
						break
			if not obj:
				return (404, None) #_("Container not found")

			if obj.parent != None:
				return (404, None)# _("This is not a top level container")

			if "1" == system_options["server_license_type"] and request_object.number_of_connections >= len(obj.get_all_children()):
				return (503, None)

			# set content type of container
			if obj.type.http_content_type is "":
				return (None, _("Unknown content type"))
			request_object.add_header("Content-type", obj.type.http_content_type.lower())

			request_object.container_id = obj.id
			debug("Container id: " + obj.id)

			# execute session start action
			if not request_object.session().on_start_executed and _a.global_actions["session"]["sessiononstart"].code:
				managers.engine.special(_a, _a.global_actions["session"]["sessiononstart"])
				request_object.session().on_start_executed = True

			result = None
			try:
				result = managers.engine.render(_a, obj, None, obj.type.render_type.lower())
			except VDOM_exception, e:
				debug("Render exception: " + str(e))
				return (None, str(e))

			if request_object.fh:
				shutil.copyfileobj(request_object.fh, request_object.wfile)
				return (None, "")

			outp = request_object.output()
			if outp:
				if request_object.binary():
					return (None, outp)
				else:
					return (None, outp.encode("utf-8"))

			#debug("Result is: " + result.encode("utf-8"))

			# now do module post processing
#			module = VDOM_post_processing()
#			try:
#				result = module.run(result)
#			except:
#				debug(_("Module manager: post processing error: %s") % sys.exc_info()[0])
#				traceback.print_exc(file=debugfile)
			return (None, result.encode("utf-8"))

		elif "py" == request_type:	# dynamic python script, this doesn't require an application to be registered
			try:
				module = VDOM_module_python()
				return (None, module.run(request_object))
			except Exception, e:
				debug(_("Module manager: python module error: %s") % str(e))
				#traceback.print_exc(file=debugfile)
				return (500, None)

		elif request_type:# pass to resource module
			module = VDOM_module_resource()
			ret = module.run(request_object, request_type)
			return (None, ret) if ret else (404, None)

		return (404, None)


module_manager_internal = VDOM_module_manager()
del VDOM_module_manager
