import managers, collections, xml.dom.minidom
from extracter import VDOM_extracter
from subprocess import *
import shlex

class VDOM_restore(object):
    
    def restore(self, driver, app_id, revision_number):
        extracters = VDOM_extracter.get_extracters(app_id)
	dirs= {}
	driver_path = driver.mount()
	ok = True
        for key in extracters:
	    dirname = key
            dirs[key] = extracters[key].get_restore_path()
            
        
        
	    """
          Here should be instructions, that excec bash scripts to restore. For example:
          ---------------------------------------------------------------
             Popen(command, driver_path, app_id, revision_number, dirs)
             -p 		Driver path
             -g 		App-GUID
             -r 		REV_NUMBER
             --application 	Where to put app.xml
             and so on
          ---------------------------------------------------------------
	  """
	    from utils.card_connect import send_to_card_and_wait
	    result = send_to_card_and_wait("getlicense %s %s" % ("0", "114"),"%s/%s" % ("0", "114"))
	    crypto_arg=""
	    if not result:
		# default password
		crypto_arg="--passphrase vdom"
	    else:
		# password from PC/SC
		crypto_arg="--passphrase %s" % result	
	    debug("Crypto argument :: %s" % crypto_arg)
	    debug("Restore after DIRS and DIRNAME or smth")
	    cmd = """sh /opt/boot/do_restore.sh --mountpoint %s --guid %s --revision %s -n %s -p %s %s"""%(driver_path, app_id, revision_number, dirname, dirs[dirname], crypto_arg)
	    debug("""sh /opt/boot/do_restore.sh --mountpoint %s --guid %s --revision %s -n %s -p %s %s"""%(driver_path, app_id, revision_number, dirname, dirs[dirname], crypto_arg))
	    out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
	    out.wait()
	    rc = out.returncode
    
	    if rc == 0:
		if dirname in extracters:
		    try: 
			extracters[dirname].restore(dirs[dirname])
		    except: 
			debug("Error: %s has not restored" % dirname)
			ok = False
	    else:
		debug(str(out.stderr.read()))
		debug("Error: %s has not restored" % dirname)
		ok = False
	if not ok:
	    exit_error = "Some parts of application (id = %s) has not restored" % app_id
	    debug(exit_error)
	driver.umount()
	    
            
    def list_apps(self, driver_path):
	
	cmd = """sh /opt/boot/repo_browse.sh -L -p %s """%(driver_path)
	out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
	out.wait()
	rc = out.returncode

	if rc == 0:
	    xml_doc = str(out.stdout.read())
	else:
	    return False
    
	app_list = collections.OrderedDict()
	dom = xml.dom.minidom.parseString(xml_doc)
	node_list = dom.getElementsByTagName('Application')
	for node in node_list:
	    key = node.getElementsByTagName('ID')[0].childNodes[0].data
	    value = node.getElementsByTagName('Name')[0].childNodes[0].data
	    app_list[key] = value
	return app_list
    
    def revisions(self, driver_path, app_id):
	
	cmd = """sh /opt/boot/repo_browse.sh -L -g %s -p %s """%(app_id, driver_path)
	out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
	out.wait()
	rc = out.returncode

	if rc == 0:
	        xml_doc = str(out.stdout.read())
	else:
	        return False
	rev_list = []
	dom = xml.dom.minidom.parseString(xml_doc)
	node_list = dom.getElementsByTagName('Information')
	for node in node_list:
	    rev_list.append({"id": node.getElementsByTagName('ID')[0].childNodes[0].data,
	                     "revision": node.getElementsByTagName('RevisionNumber')[0].childNodes[0].data,
	                     "application": node.getElementsByTagName('Name')[0].childNodes[0].data,
	                     "time": node.getElementsByTagName('BackupTime')[0].childNodes[0].data})
	rev_list.sort(key=lambda rev: int(rev["revision"]))
	return rev_list 
	    
    
    def revision_info(self, driver_path, app_id, revision_number):
        """
          Here should be instructions, that excec bash scripts, that
          return information about revision
        """
	cmd = """sh /opt/boot/repo_browse.sh -p %s -g %s -i %s """%(driver_path, app_id, revision_number)
	out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
	out.wait()
	rc = out.returncode

	if rc == 0:
	    xml_doc = str(out.stdout.read())
	else:
	    return False
	    
	dom = xml.dom.minidom.parseString(xml_doc)
	rev_info = {"id": dom.getElementsByTagName('ID')[0].childNodes[0].data,
	            "name": dom.getElementsByTagName('Name')[0].childNodes[0].data,
	            "description": dom.getElementsByTagName('Description')[0].childNodes[0].data,
	            "owner": dom.getElementsByTagName('Owner')[0].childNodes[0].data,
	            "active": dom.getElementsByTagName('Active')[0].childNodes[0].data,
	            "server_version": dom.getElementsByTagName('Serverversion')[0].childNodes[0].data,
	            "current_server": dom.getElementsByTagName('CurrentServer')[0].childNodes[0].data,
	            "virtual_hosts": dom.getElementsByTagName('VirtualHosts')[0].childNodes[0].data if dom.getElementsByTagName('VirtualHosts')[0].childNodes else "",
	            "scripting_language": dom.getElementsByTagName('ScriptingLanguage')[0].childNodes[0].data,
	            "icon": dom.getElementsByTagName('Icon')[0].childNodes[0].data,
	            "backup_time": dom.getElementsByTagName('BackupTime')[0].childNodes[0].data}
	return rev_info