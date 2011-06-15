"""application management module allows install, export applications etc"""
import sys, os, tempfile, zipfile, shutil, re

import managers
from utils.exception import VDOM_exception
from file_access.manager import databases_path, resources_path

rexp = re.compile(r"\<id\>(.+)\<\/id\>", re.IGNORECASE)

def import_application(path, ext = "xml"):
	"""pass the path to a zip or xml file"""
	#ext = path.split(".").pop().lower()
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
		ret = managers.xml_manager.import_application(thepath)
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
		managers.xml_manager.uninstall_application(appid)
	except Exception, e:
		import traceback
		traceback.print_exc(file=debugfile)
		return "Error: " + str(e)
	return None

def update_application(path, vh):
	appid = ""
	tmpdir = ""					# directory for saving databases
	tmpdir1 = ""				# directory for saving resources
	tmpdir_app = ""				# directory for saving application
	err_mess = ""
	try:
		f = open(path, "rb")
		some = f.read(1024)
		f.close()
		ret = rexp.search(some)
		if ret:
			appid = ret.groups()[0].strip()
			debug("Update application id=\"%s\"" % appid)
		else:
			raise VDOM_exception("Application XML-file is corrupted - unable to find application ID")
	
		debug("Check application...")
		err_mess = ". Try to INSTALL the new version instead of UPDATE"
		app = managers.xml_manager.get_application(appid)

		# temporal copy of installed application
		debug("Save installed version...")
		err_mess = ". Unable to save previous version of application"
		tmpdir_app = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
		managers.xml_manager.export_application(appid, "xml", tmpdir_app)
	except Exception, e:
		if tmpdir_app:
			shutil.rmtree(tmpdir_app, ignore_errors=True)
		raise VDOM_exception(str(e) + err_mess)

	names = vh.get_app_names(appid)			# virtual hosts

	# save databases in temp dir
	debug("Save current databases...")
	dbs = {}
	try:
		tmpdir = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
		dbpath = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], databases_path, appid)
		r = managers.database_manager.list_databases(appid)
		for item in r:
			try:
				obj = managers.database_manager.get_database(appid, item)
				shutil.copy2(dbpath + "/" + obj.filename, tmpdir)
				dbs[tmpdir + "/" + obj.filename] = {"id" : obj.id, "name" : obj.name, "owner": obj.owner_id, "type": "sqlite"}
				debug("Database %s saved" % obj.name)
			except: pass
	except: pass

	# save resources in temp dir
	debug("Save current resources...")
	res_numb = 0
	try:
		tmpdir1 = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
		rpath1 = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], resources_path, appid)
		lst = managers.resource_manager.list_resources(appid)
		for ll in lst:
			try:
				ro = managers.resource_manager.get_resource(appid, ll)
				if not ro.dependences:
					shutil.copy2(rpath1 + "/" + ro.filename, tmpdir1)
					res_numb += 1
			except: pass
	except: pass
	debug("%s resources saved" % str(res_numb))
	
	# uninstall application but keep databases
	debug("Uninstall current version...")
	try:
		managers.xml_manager.uninstall_application(appid, remove_db=False, remove_zero_res=False)
	except Exception, e:
		# nothing deleted (no del rights) - temp folders to be removed
		if tmpdir_app:
			shutil.rmtree(tmpdir_app, ignore_errors=True)
		if tmpdir:
			shutil.rmtree(tmpdir, ignore_errors=True)
		if tmpdir1:
			shutil.rmtree(tmpdir1, ignore_errors=True)
		raise
		
	# install new version
	debug("Install new version...")
	try:
		ret = import_application(path, path.split(".").pop().lower())
	except Exception, e:
		import traceback
		traceback.print_exc(file=debugfile)
		ret = (None, str(e))
	
	if "" == ret[0]:
		ret = (None, "Unable to install new version - previous version seems to be not removed")
		if tmpdir_app:
			shutil.rmtree(tmpdir_app, ignore_errors=True)
		if tmpdir:
			shutil.rmtree(tmpdir, ignore_errors=True)
		if tmpdir1:
			shutil.rmtree(tmpdir1, ignore_errors=True)
		return ret

	app_exist = True
	if not ret[0]:			# update error, restore previous version
		debug("Install error, restore previous version...")
		err_mess = ret[1]
		app_exist = False
		try:
			rest_path = os.path.join(tmpdir_app, "%s.xml" % appid) 
			ret = managers.xml_manager.import_application(rest_path)
			if not ret[0]:
				ret = (None, err_mess + ". " + ret[1] + ". Please, contact your dealer")
			else:
				debug("Restored successfully")
				app_exist = True
				ret = (None, err_mess + ". Previous version restored successfully")
		except Exception, e:
			import traceback
			traceback.print_exc(file=debugfile)
			ret = (None, err_mess + str(e))
	
	else:		# update successful
		debug("Installed successfully")

	if app_exist:
		# restore databases
		debug("Restore databases...")
		try:
			managers.database_manager.delete_database(appid)
		except: pass
		for path in dbs:
			try:
				f = open(path, "rb")
				data = f.read()
				f.close()
				managers.database_manager.add_database(appid, dbs[path], data)
			except: pass

		# restore resources
		debug("Restore resources...")
		try: os.mkdir(rpath1)
		except: pass
		r2 = os.listdir(tmpdir1)
		for item in r2:
			try:
				shutil.copy2(os.path.join(tmpdir1,item), os.path.join(rpath1,item))
			except:pass
	
		debug("Restore virtual hosts...")
		for n in names:
			vh.set_site(n, appid)
			debug("%s restored" % n)

	if tmpdir_app:
		shutil.rmtree(tmpdir_app, ignore_errors=True)
	if tmpdir:
		shutil.rmtree(tmpdir, ignore_errors=True)
	if tmpdir1:
		shutil.rmtree(tmpdir1, ignore_errors=True)
	return ret

