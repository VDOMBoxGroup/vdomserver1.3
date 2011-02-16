
import time, os, tempfile, shutil, re, base64, sys

import managers
from file_access.manager import application_path, application_file_name
from utils.exception import VDOM_exception

re_id = re.compile(r"\s+id\s*=\s*\"(.+?)\"", re.IGNORECASE)
re_type = re.compile(r"\s+type\s*=\s*\"(.+?)\"", re.IGNORECASE)
re_name = re.compile(r"\s+name\s*=\s*\"(.+?)\"", re.IGNORECASE)

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
		self.id = appid[1:].strip()
		if not self.id:
			shutil.rmtree(tmp, ignore_errors=True)
			raise VDOM_exception("Incorrect application format")
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
		shutil.rmtree(tmp, ignore_errors=True)
		t3 = time.time()
		print "Total install time:", t3-t1

	def __res(self, i, tmp):
		fa = None
		fd = None
		try:
			fa = open(os.path.join(tmp, "ra_%d" % i), "rt")
			fd = open(os.path.join(tmp, "rd_%d" % i), "rt")
		except:
			return False
		attrs = fa.read()
		fa.close()
		data = fd.read()
		fd.close()
		if not attrs or not data:
			return True
		data = data[1:].strip()

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

#		print res_id, res_name, res_type, len(data)

		_i = 0
		_j = len(data)
		x = data[0:8]
		y = data[-3:]
		if "![cdata[" == x.lower():
			_i = 8
		if "]]>" == y:
			_j = -3

		# save resource data
		attributes = {
			"id" : res_id,
			"name" : res_name.decode("utf-8"),
			"res_format": res_type
		}
		debug("Resource %s" % res_id)
		if not managers.resource_manager.check_resource(self.id, attributes):
			debug("add")
			# unbase64
			bindata = base64.b64decode(data[_i:_j])
			managers.resource_manager.add_resource(self.id, None, attributes, bindata)
		else:
			debug("exists")
		return True
