import getopt, sys, os

from utils.threads import VDOM_thread
from optparse import OptionParser
from wsgidav.wsgidav_app import DEFAULT_CONFIG
from wsgiref.simple_server import make_server
try:
	from wsgidav.version import __version__
	from wsgidav.wsgidav_app import WsgiDAVApp
except ImportError, e:
	raise RuntimeError("Could not import wsgidav package:\n%s\nSee http://wsgidav.googlecode.com/." % e)
from vdom_dav_provider import VDOM_Provider
from domain_controller import VDOM_domain_controller


class VDOM_webdav_server_thread(VDOM_thread):


	def __init__(self):
		VDOM_thread.__init__(self, name="WebDAV Server")
		self.__server = None    

	def main(self):
		sys.stderr.write("Start %s\n"%self.name)
		config = DEFAULT_CONFIG.copy()
		config.update({"host": VDOM_CONFIG["SERVER-ADDRESS"],
		               "port": VDOM_CONFIG["SERVER-DAV-PORT"],
		               "propsmanager": True,
		               "provider_mapping": {"/": VDOM_Provider()},
		               "domaincontroller": VDOM_domain_controller(), # None: domain_controller.WsgiDAVDomainController(user_mapping)
		               "acceptbasic": True,      # Allow basic authentication, True or False
		               "acceptdigest": False,     # Allow digest authentication, True or False
		               "defaultdigest": False,
		               "verbose": 0,
		               })
		app = WsgiDAVApp(config)

		# Try running WsgiDAV inside the following external servers:

		self.__server=make_server(config["host"], config["port"], app)	


		self.__server.daemon_threads=True
		self.__server.serve_forever()

	def stop(self):
		sys.stderr.write("Stop %s\n"%self.name)
		if self.__server: self.__server.shutdown()

