
import managers
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	request.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
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
  background-image:url(../images/picto-user.jpg);
  background-repeat: no-repeat;
  background-position: 0% 65%;
  margin:0px;
  padding-left: 15px;

}
-->
</style>
</head>

<body topmargin="2">
<p class="Texte"><a href="users.py">Users</a> &gt; Select user</p>
<script type="text/javascript">
var ListUserGestion = new Array();
ListUserGestion[0] = new Array();
ListUserGestion[1] = new Array();
ListUserGestion[2] = new Array();
ListUserGestion[3] = new Array();
var ListUser = new Array();
ListUser[0] = new Array();
ListUser[1] = new Array();
ListUser[2] = new Array();
ListUser[3] = new Array();

function add_li(sId, inc, NameTab) {
	var oUl = document.getElementById(sId);
	var iLength = oUl.getElementsByTagName("li").length;
	var oLi = document.createElement('li');
	var oLink = document.createElement("a");
	oLink.href = "users-modif-user.py?uid=" + eval(NameTab + '[0][' + inc + ']');
	var LkText = document.createTextNode(" " + eval(NameTab + '[1][' + inc + ']'));
	var oText = document.createTextNode(" " + eval(NameTab + '[2][' + inc + ']') + " " + eval(NameTab + '[3][' + inc + ']'));
	oLink.appendChild(LkText);
	oLi.appendChild(oLink);
	oLi.appendChild(oText);
	oUl.appendChild(oLi);
	return oLi;
}

""")
	userlist = managers.user_manager.get_all_users()
	CptTUG = 0
	CptTUA = 0
	for u in userlist:
		if u.system:
			request.write('ListUserGestion[0][%s]="%s";' % (CptTUG, u.id))
			request.write('ListUserGestion[1][%s]="%s";' % (CptTUG, u.login))
			request.write('ListUserGestion[2][%s]="%s";' % (CptTUG, u.first_name))
			request.write('ListUserGestion[3][%s]="%s";' % (CptTUG, u.last_name))
			CptTUG += 1
		else:
			request.write('ListUser[0][%s]="%s";' % (CptTUA, u.id))
			request.write('ListUser[1][%s]="%s";' % (CptTUA, u.login))
			request.write('ListUser[2][%s]="%s";' % (CptTUA, u.first_name))
			request.write('ListUser[3][%s]="%s";' % (CptTUA, u.last_name))
			CptTUA += 1
	request.write("""</script>
<div style="overflow:auto; width:630px; height:200px; border:0px #000000 solid;">
<table border="0">
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
</table>
</div>
<script type="text/javascript">
for(i=0; i<ListUserGestion[0].length; i++){
	add_li('ListUG',i,'ListUserGestion');
};
for(i=0; i<ListUser[0].length; i++){
	add_li('ListUA',i,'ListUser');
};
</script>""")
	request.write('<script type="text/javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')
	request.write("""</body>
</html>""")
