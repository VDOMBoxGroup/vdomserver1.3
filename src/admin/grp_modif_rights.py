
import managers
from util.exception import VDOM_exception
from security import *

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
		args = request.arguments().arguments()
		if "uid" in args and "" != args["uid"][0]:
			_uid = args["uid"][0]
			user = managers.user_manager.get_user_by_id(_uid)
			if not user:
				_uid = None
		if "appid" in args and "" != args["appid"][0]:
			_appid = args["appid"][0]
			try:
				app = managers.xml_manager.get_application("-".join(_appid.split("_")))
			except: pass
		if "oid" in args and "" != args["oid"][0]:
			_oid = args["oid"][0]
		if "_set" in args:
			_set = True
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
						managers.acl_manager.remove_access(appid, user.login, ac)
					elif 1 == _type or 2 == _type:
						managers.acl_manager.remove_access(objid, user.login, ac)
				for key in args.keys():
					if key.startswith("_set_"):
						idx = 0
						try: idx = int(key[5:])
						except: pass
						if idx in access:
							if 0 == _type or 3 == _type:
								managers.acl_manager.add_access(appid, user.login, idx)
							elif 1 == _type or 2 == _type:
								managers.acl_manager.add_access(objid, user.login, idx)
		if _uid and (_appid or "vdombox" == _appid) and _oid and not _set:
			_left = ""
			_right = ""
			appid = "-".join(_appid.split("_"))
			objid = "-".join(_oid.split("_"))
			_type = -1
			if app:
				if _appid == _oid:
					_left = "User: %s<br>Application: %s" % (user.login.decode("utf-8"), app.name.encode("utf-8"))
					_left = _left.encode("utf-8")
					_type = 0 # application
				else:
					obj = app.search_object(objid)
					if obj:
						_left = "User: %s<br>Object: %s" % (user.login.decode("utf-8"), obj.name.encode("utf-8"))
						_left = _left.encode("utf-8")
						if "1" == str(obj.type.container): _type = 1 # simple object
						else: _type = 2 # container
			elif "vdombox" == _appid:
				_left = "User: %s<br>Access to VDOM Box" % user.login.decode("utf-8")
				_left = _left.encode("utf-8")
				_type = 3 # server
			if -1 != _type:
				access = []
				if 0 == _type: access = access_to_application
				elif 1 == _type: access = access_to_simple_object
				elif 2 == _type: access = access_to_container_object
				elif 3 == _type: access = access_to_server
				for ac in access:
					txt = all_access[ac]
					checked = ""
					_name = "_set_"
					if 0 == _type or 3 == _type:
						if managers.acl_manager.check_access(appid, user.login, ac):
							checked = "checked"
						elif managers.acl_manager.check_access2(appid, appid, user.login, ac):
							_name = "_inh_"
							checked = "checked disabled"
					elif 1 == _type or 2 == _type:
						if managers.acl_manager.check_access(objid, user.login, ac):
							checked = "checked"
						elif managers.acl_manager.check_access2(appid, objid, user.login, ac):
							_name = "_inh_"
							checked = "checked disabled"
					_right += """<input type=checkbox name="%s" value=1 %s>%s</input><br>""" % (_name + str(ac), checked, txt)
				_right += """<input type=hidden name="_set" value=1>"""

			content = """<p align="center" class="Texte-page">Modify access</p>
<form name="form1" method="post" action="/grp-modif-rights.py?uid=%s&appid=%s&oid=%s">
<table align="center" cellpadding="0" cellspacing="0">
  <TR>
    <TD width="300" align="right"><span class="Texte-page">%s</span></TD>
    <td width="50"></td>
    <TD width="400" class="Texte-page">%s</TD>
  </TR>
  <TR>
    <TD align="right"><label></label>
      <label></label></TD>
    <TD><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button2" id="button2" value="OK"/>
   </TD>
    <td width="50"></td>
  </TR>
</table>
<br>
</form>""" % (_uid, _appid, _oid, _left, _right)

		elif _uid and _appid and (not _oid or not _set):
			appid = "-".join(_appid.split("_"))

			content = """<span class="Texte-page">User: %s<br></span>""" % user.login.decode("utf-8")
			content += """<p align="center" class="Texte-page">Click on object and Modify access</p>"""

			content += """<script type="text/javascript">
				var Tree2 = new Array;"""
			content += """ Tree2[0]  = "1|0|Application (type: %s, id: %s)|grp-modif-rights-form.py?uid=%s&appid=%s&oid=%s";""" % (app.name.encode("utf-8"), appid, _uid, _appid, _appid)
			objlist = []
			TabParent = []
			cpt = 1
			for o in app.objects_list:
				objlist.append((o, 0))
			while len(objlist) > 0:
			
				(obj, indent) = objlist.pop(0)
			
				ind = indent
			
				if ind == 0:
					IdParent = ind+1
				elif ind != IndTemp:
					IdParent = TabParent[ind-1]

				IndTemp = ind
				TabParent[ind:len(TabParent)]=[cpt+1]
			
				content += """ Tree2[%s]  = "%s|%s|%s (type: %s, id: %s)|grp-modif-rights-form.py?uid=%s&appid=%s&oid=%s";""" % (cpt, cpt+1, IdParent, obj.name.encode("utf-8"), obj.type.name, obj.id, _uid, _appid, "_".join(obj.id.split("-")))
				i = 0
				cpt += 1
				for o in obj.objects_list:
					objlist.insert(i, (o, indent+1))
					i += 1
			content += """</script>

<div class="tree">
<script type="text/javascript">
	createTree(Tree2,1);
</script>
</div>"""
			content = content.encode("utf-8")

		elif _uid and (not _appid or not _oid or not _set):
			applst = managers.xml_manager.get_applications()
			cont = """<option value="vdombox">VDOM Box</option>"""
			for appid in applst:
				a = "_".join(appid.split("-"))
				o = managers.xml_manager.get_application(appid)
				cont += "<option value=%s>%s (%s)</option>" % (a, o.name.encode("utf-8"), appid)
			content = """<p align="center">Select application</p>
<form name="form1" method="post" action="/grp-modif-rights.py?uid=%s">
<table align="center" cellpadding="0" cellspacing="0">
  <TR>
    <TD align="right"><span class="Texte-page">Application:</span></TD>
    <TD><select name="appid">%s</select></TD>
  </TR>
  <TR>
    <TD align="right"><label></label>
      <label></label></TD>
    <TD><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button2" id="button2" value="OK"/>
   </TD>
  </TR>
</table>
<br>
</form>""" % (_uid, cont)


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
	font-family: Tahoma, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 12px
}
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}

.tree {
	font-family: tahoma, Geneva, Arial, Helvetica, sans-serif;
	font-size: 11px;
	padding: 5px;
	white-space: nowrap;
}
.tree img {
	border: 0px;
	height: 18px;
	vertical-align: text-bottom;
}
.tree a {
	color: #000;
	text-decoration: none;
}
.tree a:hover {
	color: #345373;
}
-->
</style>
<script type="text/javascript" src="images/tree.js"></script>
<script language="javascript">
function RedimFrm(NumT, HtFrm){
	document.getElementById('FRights' + NumT).height=HtFrm;
}
</script>
</head>

<body topmargin="2">
<p class="Texte"><a href="users.py">Users</a> &gt; <a href="grp-modif.py">Select profile</a> &gt; Profile rights</p>
<div style="overflow:auto; width:632px; height:205px; border:0px #000000 solid;">%s</div>
</body>
</html>""" % content)
