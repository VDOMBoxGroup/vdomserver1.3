
import sys, os, thread

from version import VDOM_server_version
from utils.threads import VDOM_thread
from http_server import VDOM_http_server
from http_request_handler import VDOM_http_request_handler
from wsgidav.wsgidav_app import DEFAULT_CONFIG
try:
	from wsgidav.version import __version__
	from wsgidav.wsgidav_app import WsgiDAVApp
except ImportError, e:
	raise RuntimeError("Could not import wsgidav package:\n%s\nSee http://wsgidav.googlecode.com/." % e)
from webdav_server.vdom_dav_provider import VDOM_Provider
from webdav_server.domain_controller import VDOM_domain_controller
from webdav_server.property_manager import VDOM_property_manager
import managers

class VDOM_web_server_thread(VDOM_thread):

	def __init__(self):
		VDOM_thread.__init__(self, name="Web Server")
		self.__server=None

	def main(self):
		sys.stderr.write("Start %s\n"%self.name)
		server_address=(VDOM_CONFIG["SERVER-ADDRESS"], VDOM_CONFIG["SERVER-PORT"])
		self.__server=VDOM_http_server(server_address, VDOM_http_request_handler, use_ssl = False)
		config = DEFAULT_CONFIG.copy()
		config.update({"host": VDOM_CONFIG["SERVER-ADDRESS"],
		               "port": VDOM_CONFIG["SERVER-DAV-PORT"],
		               "propsmanager": VDOM_property_manager(),
		               "provider_mapping": {"/": VDOM_Provider()},
		               "domaincontroller": VDOM_domain_controller(), # None: domain_controller.WsgiDAVDomainController(user_mapping)
		               "acceptbasic": True,      # Allow basic authentication, True or False
		               "acceptdigest": False,     # Allow digest authentication, True or False
		               "defaultdigest": False,
		               "verbose": 0,
		               })
		app = WsgiDAVApp(config)
		self.__server.set_wsgi_app(app)
		msg = "%s listening on port %s"%(VDOM_http_request_handler.server_version, VDOM_CONFIG["SERVER-PORT"])
		print (msg)
		managers.log_manager.info_server(msg, "Web server thread")
		self.__server.daemon_threads=True
		self.__server.serve_forever()

	def stop(self):
		sys.stderr.write("Stop %s\n"%self.name)
		if self.__server: self.__server.shutdown()
