import request_server
from wsgidav.wsgidav_app import DEFAULT_CONFIG
try:
	from wsgidav.wsgidav_app import WsgiDAVApp
except ImportError, e:
	raise RuntimeError("Could not import wsgidav package:\n%s\nSee http://wsgidav.googlecode.com/." % e)
from vdom_dav_provider import VDOM_Provider
from domain_controller import VDOM_domain_controller

__config = DEFAULT_CONFIG.copy()
__config.update({"host": VDOM_CONFIG["SERVER-ADDRESS"],
                       "port": VDOM_CONFIG["SERVER-DAV-PORT"],
                       "propsmanager": True,
                       "provider_mapping": {"/": VDOM_Provider()},
                       "domaincontroller": VDOM_domain_controller(), # None: domain_controller.WsgiDAVDomainController(user_mapping)
                       "acceptbasic": True,      # Allow basic authentication, True or False
                       "acceptdigest": False,     # Allow digest authentication, True or False
                       "defaultdigest": False,
                       "verbose": 0,
                       })
wsgi_app = WsgiDAVApp(__config)