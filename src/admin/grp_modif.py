
import managers
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

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
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}

li {
  font-family: tahoma;
  font-size: 100%;
  color: black;
  display: list-item;
  list-style-type: none;
  background-image:url(../images/picto-group.jpg);
  background-repeat: no-repeat;
  background-position: 0% 65%;
  margin:0px;
  padding-left: 15px;

}
-->
</style>
</head>

<body topmargin="2">
<p class="Texte"><a href="users.py">Users</a> &gt; Select profile</p>
<script language="javascript">
var ListGrpGestion = new Array();
ListGrpGestion[0] = new Array();
ListGrpGestion[1] = new Array();
var ListGrp = new Array();
ListGrp[0] = new Array();
ListGrp[1] = new Array();

function add_li(sId, inc, NameTab) {
	var oUl = document.getElementById(sId);
	var iLength = oUl.getElementsByTagName("li").length;
	var oLi = document.createElement('li');
	var oLink = document.createElement("a");
	oLink.href = "grp-modif-grp.py?uid=" + eval(NameTab + '[0][' + inc + ']');
	var LkText = document.createTextNode(" " + eval(NameTab + '[1][' + inc + ']'));
	oLink.appendChild(LkText);
	oLi.appendChild(oLink);
	oUl.appendChild(oLi);
	return oLi;
}

""")
	userlist = managers.user_manager.get_all_groups()
	CptTUG = 0
	CptTUA = 0
	for u in userlist:
		if u.system:
			request.write('ListGrpGestion[0][%s]="%s";' % (CptTUG, u.id))
			request.write('ListGrpGestion[1][%s]="%s";' % (CptTUG, u.login))
			CptTUG += 1
		else:
			request.write('ListGrp[0][%s]="%s";' % (CptTUA, u.id))
			request.write('ListGrp[1][%s]="%s";' % (CptTUA, u.login))
			CptTUA += 1
	request.write("""</script>
<div style="overflow:auto; width:632px; height:205px; border:0px #000000 solid;">
<table border="0">
	<tr><td align="center" class="Texte" colspan="2"><br><b>Groups</b></td></tr>
	<tr>
		<td class="Texte" valign="top">
			<ul id="ListUG">
			</ul>
		</td>
   		<td class="Texte" valign="top">
			<ul id="ListUA">
			</ul>
		</td>
	</tr>
 </table></div>
<script language="javascript">
for(i=0; i<ListGrpGestion[0].length; i++){
	add_li('ListUG',i,'ListGrpGestion');
};
for(i=0; i<ListGrp[0].length; i++){
	add_li('ListUA',i,'ListGrp');
};
</script>""")
	request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')
	request.write("""</body>
</html>""")
