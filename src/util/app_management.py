"""application management module allows install, export applications etc"""
import sys, os, tempfile, zipfile, shutil, re

import src.xml
import src.database
import src.resource
from src.util.exception import VDOM_exception
from src.file_access.manager import databases_path
from src.file_access.manager import resources_path

rexp = re.compile(r"\<id\>(.+)\<\/id\>", re.IGNORECASE)

def import_application(path):
	"""pass the path to a zip or xml file"""
	ext = path.split(".").pop().lower()
	thepath = ""
	if "xml" == ext:
		thepath = path
	elif "zip" == ext:
		# first extract zip to a temporary dir
		direct = VDOM_CONFIG["TEMP-DIRECTORY"]
		direct = tempfile.mkdtemp("", "", direct)
		zf = None
		try:
			zf = zipfile.ZipFile(path, "r")
		except:
			shutil.rmtree(direct)
			return (None, "Incorrect zip file")
		if zf.testzip():
			# bad archive
			return (None, "Test zip error")
		fullname = os.path.join(direct, "app.xml")
		file = open(fullname, "wb")
		data = zf.read("app.xml")
		file.write(data)
		file.close()
		zf.close()
		thepath = fullname
	else:
		return (None, "Unsupported format '%s', only xml and zip are supported" % ext)

	try:
		ret = src.xml.xml_manager.import_application(thepath)
	except:
		if "zip" == ext:
			shutil.rmtree(direct)
		raise
	if "zip" == ext:
		# remove temporary files
		shutil.rmtree(direct, ignore_errors=True)
	return ret

def uninstall_application(appid):
	try:
		src.xml.xml_manager.uninstall_application(appid)
	except Exception, e:
		import traceback
		traceback.print_exc(file=debugfile)
		return "Error: " + str(e)
	return None

def update_application(path, vh):
	appid = ""
	try:
		f = open(path, "rb")
		some = f.read(1024)
		f.close()
		ret = rexp.search(some)
		if ret:
			appid = ret.groups()[0].strip()
			debug("Update application id=\"%s\"" % appid)
		else:
			raise VDOM_exception("Unable to find application ID")
		app = src.xml.xml_manager.get_application(appid)
	except:
		import traceback
		traceback.print_exc(file=debugfile)
		raise
	names = vh.get_app_names(appid)
	# save databases in temp dir
	dbs = {}
	tmpdir = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
	dbpath = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], databases_path, appid)
	r = src.database.database_manager.list_databases(appid)
	for item in r:
		obj = src.database.database_manager.get_database(appid, item)
		shutil.copy2(dbpath + "/" + obj.filename, tmpdir)
		dbs[tmpdir + "/" + obj.filename] = {"id" : obj.id, "name" : obj.name, "owner": obj.owner_id, "type": "sqlite"}
	# save resources in temp dir
	tmpdir1 = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
	rpath1 = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], resources_path, appid)
	lst = src.resource.resource_manager.list_resources(appid)
	for ll in lst:
		ro = src.resource.resource_manager.get_resource(appid, ll)
		if 0 == len(ro.dependences):
			shutil.copy2(rpath1 + "/" + ro.filename, tmpdir1)
	# uninstall application but keep databases
	try:
		src.xml.xml_manager.uninstall_application(appid, remove_db=False, remove_zero_res=False)
	except Exception, e:
		import traceback
		traceback.print_exc(file=debugfile)
	# install new version
	r = import_application(path)
	if len(r) < 2:
		shutil.rmtree(tmpdir, ignore_errors=True)
		return r
	if not r[0]:
		shutil.rmtree(tmpdir, ignore_errors=True)
		return r
	for n in names:
		vh.set_site(n, appid)
	# restore databases
	src.database.database_manager.delete_database(appid)
	for path in dbs:
		f = open(path, "rb")
		data = f.read()
		f.close()
		src.database.database_manager.add_database(appid, dbs[path], data)
	shutil.rmtree(tmpdir, ignore_errors=True)
	# restore resources
	r2 = os.listdir(tmpdir1)
	for item in r2:
		shutil.copy2(tmpdir1 + "/" + item, rpath1)
	shutil.rmtree(tmpdir1, ignore_errors=True)
	return r
