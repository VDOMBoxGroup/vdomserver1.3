import managers
import json
import base64
import hashlib  
from utils.semaphore import VDOM_semaphore
def run(request):
	args = request.arguments().arguments()
	request.render_type = "e2vdom"
	auth = request.headers().headers().get("Authorization")
	if not auth:
		request.add_header("WWW-Authenticate","Basic realm=\"vdom\"")
		request.send_htmlcode(401)
		
		return
	else:
		if auth[:len("Basic ")]=="Basic ":
			user,login = base64.b64decode(auth[len("Basic "):]).split(":")
			sem = VDOM_semaphore()
			sem.lock()
			try:
				if not managers.user_manager.match_user_md5(user, hashlib.md5(login).hexdigest()):
					time.sleep(1)
					request.send_htmlcode(401)
					return
			finally:
				sem.unlock()			
	appid = args.get("appid")
	container = args.get("objid")
	action =args.get("action_name")
	xml_param = args.get("xml_param")
	xml_data = args.get("xml_data")
	sid = args.get("sid")
	if not (appid and container and action and xml_param and xml_data):
		request.write("<ERROR>Invalid params</ERROR>")
	else:
		ret = managers.dispatcher.dispatch_action(appid, container, action, xml_param,xml_data)
		request.write("<RESULT><![CDATA[%s]]></RESULT>" % ret)
