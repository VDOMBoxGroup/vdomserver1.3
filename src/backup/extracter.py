import managers, tempfile, os, utils.uuid
from utils.app_management import import_application, uninstall_application
from subprocess import *
import shlex, shutil
import collections

class VDOM_extracter(object):

	def __init__(self, app_id):
		self.app_id = app_id

	@staticmethod
	def get_extracters(app_id):
		return collections.OrderedDict([(key, value(app_id)) for key, value in e_map.items()])

	def extract(self):
		pass
	def get_restore_path(self):
		pass
	def restore(self, path):
		pass

class VDOM_app_extracter(VDOM_extracter):

	def extract(self):
		path = tempfile.mkdtemp("", "", VDOM_CONFIG["BACKUP-DIRECTORY"])

		try:
			managers.xml_manager.export_application(self.app_id, "xml", path)
			return os.path.abspath(path)
		except:
			return None

	def get_restore_path(self):
		xml_path = tempfile.mkdtemp("", "", VDOM_CONFIG["BACKUP-DIRECTORY"])
		return os.path.abspath(xml_path)

	def restore(self, path):
		"""import app_xml"""
		if os.path.exists(path):
			try:
				appl = managers.xml_manager.get_application(self.app_id)
				uninstall_application(appl.id, remove_db = True, remove_zero_res = True, remove_storage = True, remove_ldap = True)
			except Exception as e:
				debug(unicode(e))                
			import_application(os.path.join(path, self.app_id+".xml"))
		else:
			pass

class VDOM_repo_info_extracter(VDOM_extracter):

	def extract(self):
		appl = managers.xml_manager.get_application(self.app_id)
		xml = """<?xml version="1.0" encoding="utf-8"?>
<Application>
    <ID>%(id)s</ID>
    <Name>%(name)s</Name>
</Application>""" % {"id": appl.id, "name": appl.name}
		path = tempfile.mkdtemp("", "", VDOM_CONFIG["BACKUP-DIRECTORY"])
		file = open(os.path.join(path, "metadata.xml"), "wb")
		file.write(xml)
		file.close()
		return os.path.abspath(path)

class VDOM_app_info_extracter(VDOM_extracter):

	def extract(self):
		import version
		from datetime import datetime
		#from web import virtual_hosts
		appl = managers.xml_manager.get_application(self.app_id)
		current_server = version.VDOM_server_version
		backup_time = datetime.now().isoformat()
		vh = managers.virtual_hosts
		sites = vh.get_sites()
		vh_list = []
		for site in sites:
			siteid = vh.get_site(site)
			if self.app_id == siteid:
				vh_list.append(site)
		vhosts = ", ".join(vh_list) if vh_list else ""
		xml = """<?xml version="1.0" encoding="utf-8"?>
<Information>
    <ID>%(id)s</ID>
    <Name>%(name)s</Name>
    <Description>
        %(description)s
    </Description>
    <Owner>%(owner)s</Owner>
    <Active>%(active)s</Active>
    <Serverversion>%(server_version)s</Serverversion>
    <CurrentServer>%(current_server)s</CurrentServer>
    <VirtualHosts>%(vhosts)s</VirtualHosts>
    <ScriptingLanguage>%(scripting_language)s</ScriptingLanguage>
    <Icon>%(icon)s</Icon>
    <RevisionNumber>REV</RevisionNumber>
    <Size>SIZE</Size>
    <Duptime>DUPTIME</Duptime>
    <Isfull>ISFULL</Isfull>
    <BackupTime>%(backup_time)s</BackupTime>
</Information>""" % {"id": appl.id,
		     "name": appl.name,
		     "description": appl.description,
		     "owner": appl.owner,
		     "active": appl.active,
		     "server_version": appl.server_version,
		     "current_server": current_server,
		     "vhosts": vhosts,
		     "scripting_language": appl.scripting_language,
		     "icon": appl.icon,
		     "backup_time": backup_time}
		return os.path.abspath(self.__xml_export(xml))

	def __xml_export(self, xml_data):
		path = tempfile.mkdtemp("", "", VDOM_CONFIG["BACKUP-DIRECTORY"])
		file = open(os.path.join(path, self.app_id + ".xml"), "wb")
		file.write(xml_data.encode("utf-8"))
		file.close()
		return path

class VDOM_file_storage_extracter(VDOM_extracter):

	def extract(self):
		if os.path.exists(os.path.join(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"], self.app_id)):
			path = os.path.join(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"], self.app_id)
			return path
		else:
			return None

	def get_restore_path(self):
		path = os.path.join(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"], self.app_id)
		if os.path.exists(path):
			shutil.rmtree(path)
		return os.path.abspath(path)


class VDOM_ldap_extracter(VDOM_extracter):

	def extract(self):
		path = tempfile.mkdtemp("", "", VDOM_CONFIG["BACKUP-DIRECTORY"])
		cmd = """sh /opt/boot/ldap_backup.sh -g %s -b -o %s""" % (self.app_id, os.path.abspath(path))
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode
		if rc == 0:
			return os.path.abspath(path)
		else:
			debug(str(out.stderr.read()))
			return None

	def get_restore_path(self):
		path = tempfile.mkdtemp("", "", VDOM_CONFIG["BACKUP-DIRECTORY"])
		return os.path.abspath(path)

	def restore(self, path):
		cmd = """sh /opt/boot/ldap_backup.sh -g %s -r -i %s""" % (self.app_id, path)
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode
		if rc == 0:
			return True
		else:
			debug(str(out.stderr.read()))
			return None

class VDOM_share_extracter(VDOM_extracter):

	def extract(self):
		if os.path.exists(VDOM_CONFIG["SHARE-DIRECTORY"]):
			path = os.path.abspath(VDOM_CONFIG["SHARE-DIRECTORY"])
			return path
		else:
			return None

	def get_restore_path(self):
		path = os.path.abspath(VDOM_CONFIG["SHARE-DIRECTORY"])
		if os.path.exists(path):
			shutil.rmtree(path)
		return path

class VDOM_xapian_extracter(VDOM_extracter):

	def extract(self):
		path = ""
		appl = managers.xml_manager.get_application(self.app_id)
		for obj in appl.get_objects_list():
			if obj.type.id == '3187104f-f42c-4f7d-a8df-956fbff94948':
				path = os.path.abspath(os.path.join(VDOM_CONFIG["BACKUP-DIRECTORY"], str(obj.id)))
		if os.path.exists(path):
			return path
		else:
			return None

	def get_restore_path(self):
		path = ""
		appl = managers.xml_manager.get_application(self.app_id)
		for obj in appl.get_objects_list():
			if obj.type.id == '3187104f-f42c-4f7d-a8df-956fbff94948':
				path = os.path.abspath(os.path.join(VDOM_CONFIG["BACKUP-DIRECTORY"], str(obj.id)))
		if os.path.exists(path):
			shutil.rmtree(path)
		if path:
			return path


e_map = collections.OrderedDict([("application", VDOM_app_extracter),
                                 ("storage", VDOM_file_storage_extracter),
                                 ("share", VDOM_share_extracter),
                                 ("ldap", VDOM_ldap_extracter),
                                 ("xapian", VDOM_xapian_extracter),
                                 ("rev_metadata", VDOM_app_info_extracter),
                                 ("repo_metadata", VDOM_repo_info_extracter)])