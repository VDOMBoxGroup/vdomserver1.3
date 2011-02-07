
import src.xml
import src.managers
from src.util.exception import VDOM_exception
from src.security import *

def run(request):
	sess = request.session()
	content = ""
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		_uid = None
		_appid = None
		_oid = None
		_set = None
		user = None
		app = None
		NbTree = None
		args = request.arguments().arguments()
		if "uid" in args and "" != args["uid"][0]:
			_uid = args["uid"][0]
			user = src.managers.user_manager.get_user_by_id(_uid)
			if not user:
				_uid = None
		if "appid" in args and "" != args["appid"][0]:
			_appid = args["appid"][0]
			try:
				app = src.xml.xml_manager.get_application("-".join(_appid.split("_")))
			except: pass
		if "oid" in args and "" != args["oid"][0]:
			_oid = args["oid"][0]
		if "_set" in args:
			_set = True
		if "NbTree" in args and "" != args["NbTree"][0]:
			NbTree = args["NbTree"][0]
		if "vdombox" == _appid:
			_oid = _appid

		if _uid and _appid and _oid and _set:
			appid = "-".join(_appid.split("_"))
			objid = "-".join(_oid.split("_"))
			_set = None
			_type = -1
			if app:
				if _appid == _oid:
					_type = 0 # application
				else:
					obj = app.search_object(objid)
					if obj:
						if "1" == str(obj.type.container): _type = 1 # simple object
						else: _type = 2 # container
			elif "vdombox" == _appid:
				_type = 3 # server
			if -1 != _type:
				access = []
				if 0 == _type: access = access_to_application
				elif 1 == _type: access = access_to_simple_object
				elif 2 == _type: access = access_to_container_object
				elif 3 == _type: access = access_to_server
				for ac in access:
					if 0 == _type or 3 == _type:
						src.managers.acl_manager.remove_access(appid, user.login, ac)
					elif 1 == _type or 2 == _type:
						src.managers.acl_manager.remove_access(objid, user.login, ac)
				for key in args.keys():
					if key.startswith("_set_"):
						idx = 0
						try: idx = int(key[5:])
						except: pass
						if idx in access:
							if 0 == _type or 3 == _type:
								src.managers.acl_manager.add_access(appid, user.login, idx)
							elif 1 == _type or 2 == _type:
								src.managers.acl_manager.add_access(objid, user.login, idx)
		if _uid and (_appid or "vdombox" == _appid) and _oid and not _set:
			_left = ""
			_right = ""
			appid = "-".join(_appid.split("_"))
			objid = "-".join(_oid.split("_"))
			_type = -1
			if app:
				if _appid == _oid:
					_left = "User: %s<br>Application: %s" % (user.login, app.name.encode("utf-8"))
					_type = 0 # application
				else:
					obj = app.search_object(objid)
					if obj:
						_left = "User: %s<br>Object: %s" % (user.login, obj.name.encode("utf-8"))
						if "1" == str(obj.type.container): _type = 1 # simple object
						else: _type = 2 # container
			elif "vdombox" == _appid:
				_left = "User: %s<br>Access to VDOM Box" % user.login
				_type = 3 # server
			if -1 != _type:
				access = []
				if 0 == _type: access = access_to_application
				elif 1 == _type: access = access_to_simple_object
				elif 2 == _type: access = access_to_container_object
				elif 3 == _type: access = access_to_server
				cptln = 0
				for ac in access:
					txt = all_access[ac]
					checked = ""
					_name = "_set_"
					if 0 == _type or 3 == _type:
						if src.managers.acl_manager.check_access(appid, user.login, ac):
							checked = "checked"
						elif src.managers.acl_manager.check_access2(appid, appid, user.login, ac):
							_name = "_inh_"
							checked = "checked disabled"
					elif 1 == _type or 2 == _type:
						if src.managers.acl_manager.check_access(objid, user.login, ac):
							checked = "checked"
						elif src.managers.acl_manager.check_access2(appid, objid, user.login, ac):
							_name = "_inh_"
							checked = "checked disabled"
					_right += """<input type=checkbox name="%s" value=1 %s>%s</input><br>""" % (_name + str(ac), checked, txt)
					cptln += 1
				_right += """<input type=hidden name="_set" value=1>"""

			content = """<table border="0" cellpadding="2" cellspacing="0">
<form name="form1" method="post" action="/grp-modif-rights-form.py?uid=%s&appid=%s&oid=%s&NbTree=%s">
  <TR>
    <TD>%s</TD>
    <TD>&nbsp;<input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button2" id="button2" value="OK"/></TD>
  </TR>
</form>
</table>
<script language="javascript">
var HFrm = 20*%s+4;
parent.RedimFrm(%s,HFrm);
</script>""" % (_uid, _appid, _oid, NbTree, _right, cptln, NbTree)

	request.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Options</title>
<style type="text/css">
<!--
.Texte-page {
	font-family: Tahoma;
	font-weight: normal;
	font-size: 12px;
}
.Texte {
	font-family: tahoma, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 12px
}
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}

-->
</style>
</head>
<body topmargin="0" leftmargin="0" marginwidth="0" marginheight="0" style="font-family: tahoma; font-size: 11px;">
%s
</body>

</html>""" % content)
