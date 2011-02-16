"""python handler module"""

import os, sys, traceback

from .module import VDOM_module
from utils.exception import VDOM_exception
import admin

class VDOM_module_python(VDOM_module):
	"""process python scripts"""

	def run(self, request):
		"""run python script"""
		script_name = request.environment().environment()["SCRIPT_NAME"]
		if script_name.startswith("/"):
			script_name = script_name[1:]
		script_name = script_name.split(".")[0]
		script_name = "_".join(script_name.split("-"))
		request.add_header("Content-Type", "text/html")
		try:
			exec "admin." + script_name + ".run(request)"
		except Exception, e:
			debug("Error: %s" % str(e))
			traceback.print_exc(file=debugfile)
		return request.output()
