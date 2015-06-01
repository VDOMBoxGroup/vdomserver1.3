
import managers



def vdom_type_to_js(vdomtype, output):
	"""
	Render VDOM Type to JavaScript code
	"""
	events = vdomtype.event_info.user_interface_events + vdomtype.event_info.object_events.keys()
	events = "this.registerEvents([%s])" % ", ".join(["\"%s\"" % event for event in events]) if events else ""

	output(
	    ("function VDOM_Type_%(type)s(id, eventEngine){\n"
	      "  this.Base=VDOM_Object;\n"
	      "  this.Base(id, eventEngine);"
	      "  %(events)s"
	      "};\n"
	      "VDOM_Type_%(type)s.prototype=new VDOM_Object;") % {
	        "type": vdomtype.id.replace("-", "_"), 
	        "events": events
	    }
	)

	actions = vdomtype.action_info.get("2330fe83-8cd6-4ed5-907d-11874e7ebcf4", None) # TODO!!!
	if actions:
		for name, action in actions.iteritems():
			output(
			    "VDOM_Type_%(type)s.prototype.%(name)s=function(%(parameters)s){%(source)s}" % {
			        "type": vdomtype.id.replace("-", "_"),
			        "name": name,
			        "parameters": ("".join([", %s" %  parameter.name for parameter in action.parameters]).replace('"',r'\"') )[2:],
			        "source": action.source_code
			    }
			)

	return output


def compile_declarations_n_libraries(container):

	types = container.object.types
	containers = container.object.containers
	libraries = container.object.libraries
	
	libraries="".join(["".join(library) for library in libraries.itervalues()])
	libraries+="".join(["".join(library) for library in managers.request_manager.current.dyn_libraries.itervalues()])
	
	lines = ["EventQueue=new VDOM_EventQueue;"]
	append_lines = lines.append
	
	for type_id in containers.iterkeys():
		append_lines(
			"function VDOM_Obj_Type_%(type)s(id, eventEngine){this.Base=VDOM_Object;this.Base(id, eventEngine)};\n"\
			"VDOM_Obj_Type_%(type)s.prototype=new VDOM_Object;" % {
		        "type": type_id.replace("-", "_")
		    }
		)
	
	for type_id, type_obj in types.iteritems():
		vdom_type_to_js(type_obj, append_lines)
		
	return "\n".join(lines), libraries


def compile_registations_render_params(parameters):
	out = []
	
	for parameter in parameters:
		
		value = parameter.value.replace(r'\"', '"')
		if len(value) > 0:
			
			if value[0] == '"':
				out.append(r'\"' + value[1:-1].replace('"', r'&quot;') + r'\"')
			
			else:
				out.append(value.replace('"', r'\"'))
				
	return ','.join(out)


def compile_registations(container, parent):

	application = managers.request_manager.get_request().application()
	if container.id in application.all_dynamic_objects:
		return ""

	lines = []
	lines_append = lines.append
	
	lines_append(
		"if(typeof Obj_%(container_id)s_EventEngine!=='undefined'){Obj_%(container_id)s_EventEngine.stop();delete Obj_%(container_id)s_EventEngine;}\n"\
		"if(typeof Obj_%(container_id)s_Dispatcher!=='undefined'){delete Obj_%(container_id)s_Dispatcher;}\n"\
		"Obj_%(container_id)s_Dispatcher=new VDOM_EventDispatcher();\n"\
		"Obj_%(container_id)s_EventEngine=new VDOM_EventEngine(Obj_%(container_id)s_Dispatcher, EventQueue);" % {
	        "container_id": container.id.replace("-", "_")
	    }
	)

	lines_append(
		"function VDOM_Obj_Type_%(type_id)s(id, eventEngine){this.Base=VDOM_Object;this.Base(id, eventEngine)};\n"\
		"VDOM_Obj_Type_%(type_id)s.prototype=new VDOM_Object;" % {
	        "type_id": container.id.replace("-", "_")
	    }
	)
	
	# objects - dictionary of objects, key is object ID
	objects = container.object.get_objects()
	objects[container.id] = container.object
	
	for object_id in objects:
		#print "[E2VDOM] Container", container.id
		events = application.events_by_object.get(object_id, None)
		#print "[E2VDOM] Events", events
		
		if events:
			for event in events.itervalues():
				#print "[E2VDOM] Event", event.name
				
				for action_id in event.actions:
					#print "[E2VDOM] Action", action_id
					#print "[E2VDOM] Application actions", application.actions
					#print "[E2VDOM] Event container", event.container
					action = application.actions.get(action_id, None)
					#print "[E2VDOM] Action", action
					source = "\"o_%s:%s\"" % (
					    object_id.replace("-", "_"),
					    event.name
					)
					
					if action is None:
						# action=application.search_object(event.container).actions["id"].get(action_id, None)
						action, action_container=application.search_server_action(action_id)
						#print "[E2VDOM] Action", action
						if action is None:
							target = "\"ACHTUNG! UNKNOWN ACTION %s\""%(action_id)

						else:
							target="\"server\""
							#if action.target_object in container.object.objects:
							#	target="\"server\""
							#else:
							#	target="\"Object_%s:bubbleEvent(\"%s\")\""%(container.id.replace("-", "_"), self.name)
							#	# schedule dispatch
					else:
						#if action.target_object in container.object.objects:
						target = "\"Obj_%s:%s(%s)\"" % (
						    action.target_object.replace("-", "_"),
						    action.method_name,
							#", ".join([parameter.value.replace('"',r'\"') for parameter in action.parameters]) )
							compile_registations_render_params(action.parameters)
						)
						#print compile_registations_render_params(action.parameters)
						#else:
						#	target="\'Obj_%s:bubbleEvent(\"%s\")\'"%(container.id.replace("-", "_"), action.method_name)
					lines_append(
						"Obj_%(container)s_Dispatcher.addDispatchEvent(%(source)s, %(target)s);" % {
					        "container": container.id.replace("-", "_"),
					        "source": source,
					        "target": target
					    }
					)

	for obj in container.object.get_objects_list():
		lines_append(
			"Obj_%(object)s=new VDOM_Type_%(object_type)s(\"o_%(object)s\", Obj_%(container)s_EventEngine);" % {
		        "container": container.id.replace("-", "_"),
		        "object": obj.id.replace("-", "_"),
		        "object_type": obj.type.id.replace("-", "_")
		    }
		)

	#print "[E2VDOM] Container %s, parent %s"%(container.id, parent)
	#lines.append(
	#	"Obj_%(container)s=new VDOM_Obj_Type_%(type)s(\"o_%(container)s\", Obj_%(container)s_EventEngine);"%\
	#	{"container": container.id.replace("-", "_"), "type": container.object.type.id.replace("-", "_")})
	lines_append( # Leo
		"Obj_%(container)s=new VDOM_Type_%(type)s(\"o_%(container)s\", Obj_%(container)s_EventEngine);" % {
	        "container": container.id.replace("-", "_"),
	        "type": container.object.type.id.replace("-", "_")
	    }
	)
	
	if parent:
		lines_append(
			"Obj_%(container)s.bubbleEvent=function(e){"\
			"Obj_%(container)s.riseEvent('tfrEvent', e.parameters, Obj_%(parent)s_eventEngine);};" % {
		        "container": container.id.replace("-", "_"),
		        "parent": parent.replace("-", "_")
		    }
		)
	lines_append(
		"Obj_%(container)s_EventEngine.start();" % {
	        "container": container.id.replace("-", "_")
	    }
	)

	#lines.append("});")

	return "\n".join(lines)


def compile_dynamic_e2vdom(container, actions=None):
	"""
	Render e2vdom code for dynamic/dummy objects
	"""
	application = managers.request_manager.get_request().application()
	
	lines = []
	append_lines = lines.append

	for type_id, type_obj in container.all_types().iteritems():
		append_lines("if (!('VDOM_Type_%s' in window)){" % type_id.replace("-", "_"))
		vdom_type_to_js(type_obj, append_lines)
		append_lines("window.VDOM_Type_%(type)s = VDOM_Type_%(type)s;}" % {'type': type_id.replace("-", "_")})

	append_lines(
	    "if(typeof Obj_%(container_id)s_EventEngine!=='undefined'){Obj_%(container_id)s_EventEngine.stop();delete Obj_%(container_id)s_EventEngine;}\n"\
	    "if(typeof Obj_%(container_id)s_Dispatcher!=='undefined'){delete Obj_%(container_id)s_Dispatcher;}\n"\
	    "Obj_%(container_id)s_Dispatcher=new VDOM_EventDispatcher();\n"\
	    "Obj_%(container_id)s_EventEngine=new VDOM_EventEngine(Obj_%(container_id)s_Dispatcher, EventQueue);" % {
	        "container_id": container.id.replace("-", "_")
	    }
	)		
	
	if actions:
		# actions is dictionary like
		# {
		#   (src_obj, event): [(dst_obj, action, param1, param2, param3)]
		# }
		def parse_params(params):
			out = []
			for value in params:
				if value and value[0] == '"':
					value = r'\"%s\"' % value[1:-1].replace('"', r'&quot;')
		
				else:
					value = value.replace('"', r'\"')
					
				out.append(value)

			return ','.join(out)
	
		
		for event, actions in actions.iteritems():
			for action in actions:
				append_lines(
					"Obj_%s_Dispatcher.addDispatchEvent(\"o_%s:%s\", \"Obj_%s:%s(%s)\");" % (
					    container.id.replace("-", "_"),
					    event[0].replace("-", "_"),
					    event[1],
					    action[0].replace("-", "_"),
					    action[1],
				        parse_params(action[2:])
				    )
				)
		
	for obj in container.all_objects().itervalues():
		append_lines(
		    "Obj_%(object)s=new window.VDOM_Type_%(object_type)s(\"o_%(object)s\", Obj_%(container)s_EventEngine);" % {
		        "container": container.id.replace("-", "_"),
		        "object": obj.id.replace("-", "_"),
		        "object_type": obj.type.id.replace("-", "_")
		    }
		)
	
	append_lines(
	    "Obj_%s_EventEngine.start();" % container.id.replace("-", "_")
	)
	
	return "\n".join(lines)