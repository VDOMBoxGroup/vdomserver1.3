
import managers
from util.exception import VDOM_exception

def run(request):
	request.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Options</title>
<style type="text/css">
<!--
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 12px
}
.Texte-page {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 12px
}
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
input{
	font-family:Arial;
	font-size:x-small;
	border-width:1px;
	border-color:black;
}
-->
</style>
</head>

<body topmargin="2">""")

	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	error = ""
	obj = None
	if "uid" in args and "" != args["uid"][0]:
		uid = args["uid"][0]
		obj = managers.user_manager.get_user_by_id(uid)
		if not obj:
			error = "User doesn't exist"

	if obj and hasattr(obj, "password") and "password" in args:
		obj.password = args["password"][0]
		managers.user_manager.sync()
	elif obj and "last_name" in args and "first_name" in args and "slevel" in args and "email" in args and "" != args["last_name"][0] and "" != args["first_name"][0]:
		obj.first_name = args["first_name"][0]
		obj.last_name = args["last_name"][0]
		obj.security_level = args["slevel"][0]
		obj.email = args["email"][0]

		old_member_of = obj.member_of
		obj.member_of = []
		for key in args.keys():
			if key.startswith("group_"):
				gn = key[6:]
				group = managers.user_manager.get_user_by_id(gn)
				if group:
					obj.member_of.append(group.login)
					if obj.login not in group.members:
						group.members.append(obj.login)
		for i in old_member_of:
			if i not in obj.member_of:
				group = managers.user_manager.get_user_by_name(i)
				if obj.login in group.members:
					group.members.remove(obj.login)
		managers.user_manager.sync()
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Modifications have been registered";</script>')

	elif obj and not obj.system and "description" in args and "" != args["description"][0]:
		obj.description = args["description"][0]
		managers.user_manager.sync()
	

	request.write("""<p class="Texte"><a href="users.py">Users</a> &gt; <a href="users-modif.py">Select user</a> &gt; Update user</p>
<div style="overflow:auto; width:630px; height:205px; border:0px #000000 solid;">
<table align="center" cellpadding="2" cellspacing="0">
  <tr><td colspan="4" class="Texte-page"><b><font color="red">&nbsp;%s</font></b></td></tr>""" % error)

	sss = ""
	if obj and obj.system:
		sss = "disabled"

	if obj and hasattr(obj, "first_name"):
		request.write("""<form name="form1" method="post" action="">
  <TR>
    <TD align="right"><span class="Texte-page">Last name :&nbsp;</span></TD>
    <TD><INPUT value="%s" maxLength="50" size="20" name="last_name" %s><strong>*</strong> </TD>
  </TR>
  <TR>
    <TD align="right"><span class="Texte-page">First name :&nbsp;</span></TD>
    <TD><INPUT value="%s" maxLength="50" size="20" name="first_name" %s><strong>*</strong> </TD>
  </TR>
  <TR>
    <TD align="right"><span class="Texte-page">Login :&nbsp;</span></TD>
    <TD><INPUT value="%s" maxLength="20" name="login" disabled><strong>*</strong> </TD>
  </TR>
  <TR>
    <TD align="right"><span class="Texte-page">E-Mail :&nbsp;</span></TD>
    <TD colspan="3"><INPUT value="%s" size="30" name="email" %s></TD>
  </TR>
  <TR>
    <TD align="right"><span class="Texte-page">Security level :&nbsp;</span></TD>
    <TD><INPUT value="%s" maxLength="20" name="slevel" %s>
	</TD>
  </TR>
<INPUT value="%s" type="hidden" name="uid">
""" % (obj.last_name, sss, obj.first_name, sss, obj.login, obj.email, sss, obj.security_level, sss, obj.id))

		request.write("""<TR>
    <TD align="right"><span class="Texte-page">Groups :&nbsp;</span></TD>""")

		f = 0
		groups = managers.user_manager.get_all_groups()
		for g in groups:
			if f != 0:
				if (f % 3) == 0:
					request.write("""</tr><TR><TD></TD>""")
			s = ""
			if g.login in obj.member_of:
				s = "checked"
			request.write("""<TD style="border: solid 1px white; vertical-align: middle;" class="Texte-page"><input type=checkbox name=%s value=%s %s %s>%s</input></TD>""" % ("group_"+g.id, "1", s, sss, g.login))
			f += 1

		request.write("""</tr><TR>
    <TD></TD>
    <TD align="center"><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button2" id="button2" value="OK"/>
    <input type="button" value="Rights..." style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" onclick="document.location='/users-modif-rights.py?uid=%s'" %s/></TD>
  </TR>
</form>""" % (obj.id, sss))

		request.write("""<form name="form2" method="post" action="">
  <TR>
    <TD align="right"><span class="Texte-page">Password :&nbsp;</span></TD>
    <TD><INPUT value="" type="password" maxLength="20" name="password"></TD>
    <TD align="right"><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button4" id="button4" value="Set password"/></td>
    <INPUT value="%s" type="hidden" name="uid">
  </TR>
""" % obj.id)


	elif obj:
		request.write("""<form name="form1" method="post" action="">
  <TR>
    <TD align="right"><span class="Texte-page">Group name:</span></TD>
    <TD><INPUT value="%s" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" maxLength="50" size="30" name="group_name" disabled><strong>*</strong> </TD>
  </TR>
  <TR>
    <TD style="vertical-align: top;" align="right"><span class="Texte-page">Description:</span></TD>
    <TD><textarea style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" cols="50" rows="5" name="description" %s>%s</textarea></TD>
  </TR><INPUT value="%s" type="hidden" name="uid">
""" % (obj.login, sss, obj.description, obj.id))

		request.write("""<TR>
    <TD align="right"><label></label>
      <label></label></TD>
    <TD><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button2" id="button2" value="OK">
<input type="button" value="Rights..." style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" onclick="document.location='/grp-modif-rights.py?uid=%s'" %s/></TD>
  </TR>
</form>""" % (obj.id, sss))
	request.write("""</table>
</div>
</body>
</html>""")
