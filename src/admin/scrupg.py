
from src.util.exception import VDOM_exception
from src.server.local_server import send_to_card

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	send_to_card("tryupdate")

	request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Screen upgrade</title>
<style type="text/css">
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
</style>
</head>
<body>
<p class="Texte">Screen upgrade started</p>
</body>
</html>
""")
