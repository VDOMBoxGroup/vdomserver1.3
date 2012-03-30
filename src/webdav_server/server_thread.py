import getopt, sys, os

from utils.threads import VDOM_thread
from optparse import OptionParser
from pprint import pprint
from inspect import isfunction
from wsgidav.wsgidav_app import DEFAULT_CONFIG
from wsgidav import util
from wsgiref.simple_server import make_server
try:
    from wsgidav.version import __version__
    from wsgidav.wsgidav_app import WsgiDAVApp
    from wsgidav.fs_dav_provider import FilesystemProvider
except ImportError, e:
    raise RuntimeError("Could not import wsgidav package:\n%s\nSee http://wsgidav.googlecode.com/." % e)
from vdom_dav_provider import VDOM_Provider
from domain_controller import VDOM_domain_controller

provider_mapping = {}
user_mapping = {}


def addShare(shareName, davProvider):
    provider_mapping[shareName] = davProvider

    
def addUser(realmName, user, password, description, roles=[]):
    realmName = "/" + realmName.strip(r"\/")
    userDict = user_mapping.setdefault(realmName, {}).setdefault(user, {})
    userDict["password"] = password
    userDict["description"] = description
    userDict["roles"] = roles
    
def _readConfigFile(config_file, verbose):
    """Read configuration file options into a dictionary."""

    if not os.path.exists(os.path.abspath(config_file)):
        raise RuntimeError("Couldn't open configuration file '%s'." % config_file)
    
    try:
        import imp
        conf = {}
        configmodule = imp.load_source("configuration_module", config_file)

        for k, v in vars(configmodule).items():
            if k.startswith("__"):
                continue
            elif isfunction(v):
                continue
            conf[k] = v               
    except Exception, e:
#        if verbose >= 1:
#            traceback.print_exc() 
        exceptioninfo = traceback.format_exception_only(sys.exc_type, sys.exc_value) #@UndefinedVariable
        exceptiontext = ""
        for einfo in exceptioninfo:
            exceptiontext += einfo + "\n"   
#        raise RuntimeError("Failed to read configuration file: " + config_file + "\nDue to " + exceptiontext)
        print >>sys.stderr, "Failed to read configuration file: " + config_file + "\nDue to " + exceptiontext
        raise
    
    return conf

def _initConfig():
    """Setup configuration dictionary from default, command line and configuration file."""

    # Set config defaults
    config = DEFAULT_CONFIG.copy()

    # Configuration file overrides defaults
    config_file = os.path.join(VDOM_CONFIG["STORAGE-DIRECTORY"], "wsgidav.conf")
    if config_file: 
	fileConf = _readConfigFile(config_file, 0)
	config.update(fileConf)
    

    if not config["provider_mapping"]:
	print >>sys.stderr, "ERROR: No DAV provider defined. Try --help option."
	sys.exit(-1)
#        raise RuntimeWarning("At least one DAV provider must be specified by a --root option, or in a configuration file.")


    return config

class VDOM_webdav_server_thread(VDOM_thread):
    
    
    def __init__(self):
        VDOM_thread.__init__(self, name="WebDAV Server")
        self.__server = None    

    def main(self):
        sys.stderr.write("Start %s\n"%self.name)
	#addShare("tmp", FilesystemProvider(r"C:\Temp", readonly=True))
	#addShare("dav", VDOM_Provider(r"491d4c93-4089-4517-93d3-82326298da44"))
	#addUser("tmp", "tester", "tester", "")
	#addUser("dav", "tester2", "tester2", "")
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
	
    