
import sys, threading, imp, pkgutil

class VDOM_metaimporter(object):
	
	def __init__(self):
		sys.path.append(VDOM_CONFIG["LIB-DIRECTORY"])

	def find_module(self, fullname, path=None):
		#print "[MetaImporter] Search for %s (%s)"%(fullname, path)
		application=getattr(threading.currentThread(), "application", None)
		if application is None:
			return None
		
		if not fullname.startswith(application):
			return None
		
		if fullname == application:
			#load application
			search_path=[VDOM_CONFIG["LIB-DIRECTORY"]]
			try:
				file, pathname, description=imp.find_module(fullname, search_path)
			except ImportError, error:
				return None
			return pkgutil.ImpLoader(fullname, file, pathname, description)
		elif fullname.find(".") != -1:
			#load library
			(app_module, library) = fullname.split(".",1)
			search_path=["%s/%s"%(VDOM_CONFIG["LIB-DIRECTORY"],app_module)]
			try:
				file, pathname, description=imp.find_module(library, search_path)
			except ImportError, error:
				return None
			return pkgutil.ImpLoader(fullname, file, pathname, description)
		else:
			return None

