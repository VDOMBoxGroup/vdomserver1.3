
import managers
from memory.event import VDOM_client_server_events
import json
from StringIO import StringIO

def run(request):
	args = request.arguments().arguments()
	request.render_type = "e2vdom"
	datafield = args.get("datafield")
	sid = args.get("sid")
	if datafield:
		datafield = datafield[0]
	if sid and datafield:
#		debug(sid)
#		debug(datafield)
		# parse event data
		request.request_type = "action"
#		debug(datafield)
		ev = VDOM_client_server_events(datafield)
		app = request.application()
		if app is None:
			request.set_application_id(ev.appid)
			app = request.application()
		if app.id != ev.appid:
			debug("Event: Application mismatch")

		elif sid != ev.sid:
			debug("Event: Session mismatch")
			# # something response to client //leo
			# request.add_header("Content-Type", "text/xml")
			# rr = """<OBJECT ID="%s"><![CDATA[<script type="text/javascript">location.reload(true)</script>]]></OBJECT>\n""" % (key)
			# request.write("<ACTIONS>\n%s</ACTIONS>" % rr.encode("utf-8"))
			#sorry, its stupid idea

			rr = "<SESSIONISOVER/>"
			request.write("<ACTIONS>%s</ACTIONS>" % rr.encode("utf-8"))

		else:
			#request.add_header("Content-Type", "text/xml")
			request.add_header("Content-Type", "text/plain")
			r = {}
			err = None
			try:
				for ob, nm in ev.events:
	#				debug(ob)
	#				debug(nm)
	#				debug(str(ev.events[ob, nm]))
					obj = app.search_object(ob)
					if obj is None:
						debug("Event: Incorrect source object")
						continue
					_id = ob
					if obj.parent:
						_id = obj.parent.id
	#				h = app.events.get(_id, None)
	#				if h is None:
	#					debug("Event: No event for this container")
	#					continue
					h = app.events_by_object.get(ob, None)
	#				h = h.get(ob, None)
					if h is None:
						debug("Event: No event with this source object")
						continue
					h = h.get(nm, None)
					if h is None:
						debug("Event: No event with this name")
						continue
					#cont = app.search_object(h.container)
					#if cont is None:
					#	debug("Event: Wrong container")
					#	continue
					for a_id in h.actions:
						(_a, _obj) = app.search_server_action(a_id)
						if _a and _obj:
						#if a_id in cont.actions["id"]:
							# put parameters to the request
							params = ev.events[ob, nm]
							params["sender"] = [ob]
							request.arguments().arguments(params)
							#result = managers.engine.execute(app, cont, cont.parent, cont.actions["id"][a_id].name)
							result = managers.engine.execute(app, _obj, _obj.parent, _a.name)
							for key in result:
								k_ob=app.search_object(key)
								k_ob_parent_id = k_ob.parent.id if k_ob.parent else ""
								r[key] = (result[key],k_ob_parent_id,k_ob.type.container,k_ob.type.id)
			except Exception as e:
				import traceback
				err = StringIO()
				debug("Error: %s" % str(e))
				traceback.print_exc(file=err)

			if err:
				if VDOM_CONFIG_1["DEBUG"] == "1":
					request.write("<ERROR>%s</ERROR>"%err.getvalue().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))
				else:
					request.write('<ERROR/>')				
			else:
				if request.action_result:
					request.write(request.action_result.encode("utf-8"))
				
				rr = StringIO()
				for key in r:
					rr.write("""<OBJECT ID="%s" PARENT="%s" CONTAINER="%s" TYPE="%s"><![CDATA[%s]]></OBJECT>\n""" % (key.replace("-", "_"), r[key][1].replace("-", "_"),r[key][2],r[key][3],r[key][0]))
				request.write("<ACTIONS>%s</ACTIONS>" % rr.getvalue().encode("utf-8"))
				request.write("<SV>%s</SV>" % json.dumps(request.shared_variables).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))
			request.write("<STATE value=\"%s\" />"%0)
			
