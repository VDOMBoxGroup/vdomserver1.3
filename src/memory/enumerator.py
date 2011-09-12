"""enumerator module implements enumerating existing applications and types"""

import os, sys
import traceback

from file_access.manager import application_path # TODO: Direct use internal module variable


class VDOM_enumerator:
	"""base enumerator class"""

	def get(self):
		"""return list of items"""
		# to be implemented below
		pass


class VDOM_type_enumerator(VDOM_enumerator):
	"""type enumerator class"""

	def get(self):
		"""get type files list"""
		try:
			directory = VDOM_CONFIG["TYPES-LOCATION"]
			r1 = os.listdir(directory)
			r2 = []
			for item in r1:
				if item.endswith(".xml"):
					r2.append(os.path.join(directory, item))
			return r2
		except Exception, e:
			traceback.print_exc(file=debugfile)
			return []


class VDOM_application_enumerator(VDOM_enumerator):
	"""application enumerator class"""

	def get(self):
		"""get application files list"""
		try:
			debug("APP load debug:geting enumerator")
			directory = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], application_path)
			debug("APP load debug: app dir %s"%directory)
			r1 = os.listdir(directory)
			debug("APP load debug: app dir %s"%str(r1))
			r2 = []
			for item in r1:
				if -1 == item.find("."):
					directory2 = os.path.join(directory, item, "app.xml")
					r2.append(directory2)
					debug("APP load debug: app dir found %s"%str(directory2))
			return r2
		except Exception, e:
			traceback.print_exc(file=debugfile)
			return []
