
from util.exception import VDOM_exception
from cgi import escape

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		current = 0
		args = request.arguments().arguments()
		if "file" in args and "" != args["file"][0]:
			try:
				current = int(args["file"][0])
				if current < 0 or current > VDOM_CONFIG["LOG-FILE-COUNT"]:
					current = 0
			except: pass

		file = VDOM_CONFIG["STORAGE-DIRECTORY"] + "/log/user"
		if current > 0:
			file += "." + str(current)
		data = ""

		try:
			f = open(file, "rb")
			data = f.read()
			f.close()
		except: pass

		data = escape(data, 1)
		data = data.replace("\n", "<br>\n")

		nav = ""
		if 0 == current:
			nav = """<a href="/log-users.py?file=1">Next&gt;</a>"""
		elif VDOM_CONFIG["LOG-FILE-COUNT"] == current:
			nav = """<a href="/log-users.py?file=%d">&lt;Back</a>""" % (current - 1)
		else:
			nav = """<a href="/log-users.py?file=%d">&lt;Back</a>...<a href="/log-users.py?file=%d">Next&gt;</a>""" % (current - 1, current + 1)

		request.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Document sans nom</title>
<style type="text/css">
a:link {
	color: #000000
}
a:hover {  color: #000000; text-decoration: none}
a:visited {
	color: #000000;
}
.Texte-liens {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 10px;
}
.Texte {	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 14px;
}
</style>
</head>

<body>
<center>
<p align="left"><span class="Texte"><a href="log.py">Log</a> &gt; Users</span></p>
<p align="center"><span class="Texte">%s</span></p>
<div style="background: #eee; font-family: Tahoma; font-size: 14px;" align="left">
%s
</div>

</center>
</body>
</html>""" % (nav, data))
