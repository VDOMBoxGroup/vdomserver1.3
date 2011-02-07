
import zlib
import base64
import src.managers

def run(request):
	args = request.arguments().arguments()
	mngr = src.managers.session_manager
	sess = None
	sess = mngr[args["sid"][0]]

	if sess and "Filedata" in args:
		request.write("%s" % base64.b64encode(zlib.compress(args["Filedata"][0])))
