
import time, os, tempfile, shutil, re, base64, sys

import managers
from file_access.manager import application_path, application_file_name
from utils.exception import VDOM_exception

re_id = re.compile(r"\s*id\s*=\s*\"(.+?)\"", re.IGNORECASE)
re_type = re.compile(r"\s+type\s*=\s*\"(.+?)\"", re.IGNORECASE)
re_name = re.compile(r"\s+name\s*=\s*\"(.+?)\"", re.IGNORECASE)
re_tstamp = re.compile(r"\s+timestamp\s*=\s*\"(.+?)\"", re.IGNORECASE)

class parseapp:

	#self.work_xml_file
	#self.app_path
	#self.id

	def run(self, path):
		tmp = tempfile.mkdtemp(dir = VDOM_CONFIG["TEMP-DIRECTORY"]) + "/"
		command = 'parseapp "%s" "%s"' % (path, tmp)
		if not sys.platform.startswith("win"):
			command = "./" + command
		t1 = time.time()
		f = os.popen(command)
		f.read()
		g = f.close()
		t2 = time.time()
		if g is not None:
			shutil.rmtree(tmp, ignore_errors=True)
			raise VDOM_exception("Incorrect application format")
		print "Parse time:", t2-t1
		# read app id
		f = open(os.path.join(tmp, "appid"), "rt")
		appid = f.read()
		f.close()
		self.id = appid.strip()
		if not self.id:
			shutil.rmtree(tmp, ignore_errors=True)
			raise VDOM_exception("Incorrect application format")
		
		f = open(os.path.join(tmp, "lkeys"), "rt")
		self.key = f.read()
		f.close()
		
		# create app path
		self.app_path = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], application_path, self.id)
		self.work_xml_file = os.path.join(self.app_path, application_file_name)
		if os.path.exists(self.app_path):
			shutil.rmtree(tmp, ignore_errors=True)
			return
		managers.file_manager.create_application_skell(self.id)
		# copy app.xml
		shutil.copyfile(os.path.join(tmp, "app.xml"), self.work_xml_file)
	
		# process resources
		i = 0
		while self.__res(i, tmp):
			i += 1
	
		# process databases
		i = 0
		while self.__bas(i, tmp):
			i += 1
		
		# process embeded types
		i = 0
		while self.__emtypes(i, tmp):
			i += 1
		shutil.rmtree(tmp, ignore_errors=True)
		t3 = time.time()
		print "Total install time:", t3-t1

	def __res(self, i, tmp):
		fa = None
		fd = None
		try:
			fa = open(os.path.join(tmp, "ra_%d" % i), "rt")
			fd = open(os.path.join(tmp, "rd_%d" % i), "rb")
		except:
			return False
		attrs = fa.read()
		fa.close()
		data = fd.read()
		fd.close()
		if not attrs or not data:
			return True

		res_id = res_type = res_name = ""
		m = re_id.search(attrs)
		if m:
			res_id = m.group(1)
		m = re_name.search(attrs)
		if m:
			res_name = m.group(1)
		m = re_type.search(attrs)
		if m:
			res_type = m.group(1)
 
		x = data[0:9]
		y = data[-3:]
		if "<![cdata[" == x.lower() and "]]>" == y:
			data = data[9:-3]

		# save resource data
		attributes = {
			"id" : res_id,
			"name" : res_name.decode("utf-8"),
			"res_format": res_type
		}
		debug("Resource %s" % res_id)
		if not managers.resource_manager.check_resource(self.id, attributes):
			debug("add")
			managers.resource_manager.add_resource(self.id, None, attributes, data)
		else:
			debug("exists")
		return True

	def __bas(self, i, tmp):
		fa = None
		fd = None
		try:
			fa = open(os.path.join(tmp, "ba_%d" % i), "rt")
			fd = open(os.path.join(tmp, "bd_%d" % i), "rb")
		except:
			return False
		attrs = fa.read()
		fa.close()
		data = fd.read()
		fd.close()
		if not attrs or not data:
			return True

		bas_id = bas_type = bas_name = ""
		m = re_id.search(attrs)
		if m:
			bas_id = m.group(1)
		m = re_name.search(attrs)
		if m:
			bas_name = m.group(1)
		m = re_type.search(attrs)
		if m:
			bas_type = m.group(1)
		
		x = data[0:9]
		y = data[-3:]
		if "<![cdata[" == x.lower() and "]]>" == y:
			data = data[9:-3]

		# save resource data
		attributes = {
			"id" : bas_id,
			"name" : bas_name.decode("utf-8"),
			"owner": self.id,
			"type": bas_type
		}
		debug("Database %s" % bas_id)
		if not managers.database_manager.check_database(self.id, bas_id):
			debug("add")
			managers.database_manager.add_database(self.id, attributes, data)
		else:
			debug("exists")
		return True

	def __emtypes(self, i, tmp):
		fa = None
		fd = None
		try:
			fa = open(os.path.join(tmp, "ta_%d" % i), "rt")
			fd_name = os.path.join(tmp, "td_%d" % i)
			is_data = os.path.isfile(fd_name)
		except:
			return False
		attrs = fa.read()
		fa.close()
		if not attrs or not is_data:
			return True

		emtype_id = emtype_name = emtype_tstamp = ""
		m = re_id.search(attrs)
		if m:
			emtype_id = m.group(1)
		m = re_name.search(attrs)
		if m:
			emtype_name = m.group(1)
		m = re_tstamp.search(attrs)
		if m:
			emtype_tstamp = m.group(1)

		type_id = managers.xml_manager.test_type(fd_name)
		debug("Type loading %s" % emtype_id)
		if type_id:
			if os.stat(managers.xml_manager.get_type(emtype_id).filename)[8] < emtype_tstamp:
				debug("Replacing old type")
				# unload old type
				managers.xml_manager.unload_type(type_id)
				modulename = "module_%s"%type_id.replace('-','_')
				if modulename in sys.modules:
					sys.modules.pop(modulename)
				managers.source_cache.clear_cache()
			else:
				debug("Type is up to date")
		else:
			debug("New type")
		ret = managers.xml_manager.load_type(fd_name)
		
		return True