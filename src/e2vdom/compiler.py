
import managers


def compile_declarations_n_libraries(container):
	#lines, objects, types, containers, libraries=[], {}, {}, {}, {}
	lines, types, containers, libraries=[], container.object.types, container.object.containers, container.object.libraries
	#collect_information(container.object, objects, types, containers, libraries)

	libraries="".join(["".join(library) for library in libraries.itervalues()])

#	lines.append("jQuery(document).ready(function($){")

	lines.append("EventQueue=new VDOM_EventQueue;")
	
	for id, type in containers.iteritems():
		lines.append(
			"function VDOM_Obj_Type_%(type)s(id, eventEngine){this.Base=VDOM_Object;this.Base(id, eventEngine)};\n"\
			"VDOM_Obj_Type_%(type)s.prototype=new VDOM_Object;"%\
			{"type": id.replace("-", "_")})
	
	for id, type in types.iteritems():
		events=type.event_info.user_interface_events+type.event_info.object_events.keys()
		events=";this.registerEvents([%s])"%", ".join(["\"%s\""%event for event in events]) if events else ""
		lines.append(
			"function VDOM_Type_%(type)s(id, eventEngine){this.Base=VDOM_Object;this.Base(id, eventEngine)%(events)s};\n"\
			"VDOM_Type_%(type)s.prototype=new VDOM_Object;"%\
			{"type": id.replace("-", "_"), "events": events})
		actions=type.action_info.get("2330fe83-8cd6-4ed5-907d-11874e7ebcf4", None) # TODO!!!
		if actions:
			for name, action in actions.iteritems():
				lines.append(
					"VDOM_Type_%(type)s.prototype.%(name)s=function(%(parameters)s){%(source)s}"%\
					{"type": id.replace("-", "_"), "name": name,
					"parameters": ("".join([", %s"%parameter.name for parameter in action.parameters]).replace('"',r'\"') )[2:],
					"source": action.source_code})
	
#	lines.append("});")

	return "\n".join(lines), libraries

def compile_registations_render_params(parameters):
	a = []
	for parameter in parameters:
		x = parameter.value.replace(r'\"', '"')
		if len(x) > 0:
			if x[0] == '"':
				a.append( r'\"' + x[1:-1].replace('"', r'&quot;') + r'\"' )
			else:
				a.append( x.replace('"', r'\"') )
	return ','.join(a)

def compile_registations(container, parent):
	lines=[]

	#lines.append(";jQuery(document).ready(function($){")

	lines.append(
		"if(typeof Obj_%(container)s_EventEngine!=='undefined'){Obj_%(container)s_EventEngine.stop();delete Obj_%(container)s_EventEngine;}\n"\
		"if(typeof Obj_%(container)s_Dispatcher!=='undefined'){delete Obj_%(container)s_Dispatcher;}\n"\
		"Obj_%(container)s_Dispatcher=new VDOM_EventDispatcher();\n"\
		"Obj_%(container)s_EventEngine=new VDOM_EventEngine(Obj_%(container)s_Dispatcher, EventQueue);"%\
		{"container": container.id.replace("-", "_")})

	lines.append(
		"function VDOM_Obj_Type_%(type)s(id, eventEngine){this.Base=VDOM_Object;this.Base(id, eventEngine)};\n"\
		"VDOM_Obj_Type_%(type)s.prototype=new VDOM_Object;"%\
		{"type": container.id.replace("-", "_")})

	application=managers.request_manager.get_request().application()
	#for source_object in [container.object.get_objects(), container.object]:
	aa = container.object.get_objects()
	aa[container.id] = container.object
	for source_object in aa:
		#print "[E2VDOM] Container", container.id
		events=application.events_by_object.get(source_object, None)
		#print "[E2VDOM] Events", events
		if events:
			for event in events.itervalues():
				#print "[E2VDOM] Event", event.name
				for action_id in event.actions:
					#print "[E2VDOM] Action", action_id
					#print "[E2VDOM] Application actions", application.actions
					#print "[E2VDOM] Event container", event.container
					action=application.actions.get(action_id, None)
					#print "[E2VDOM] Action", action
					source="\"o_%s:%s\""%(source_object.replace("-", "_"), event.name)
					if action is None:
						# action=application.search_object(event.container).actions["id"].get(action_id, None)
						action, action_container=application.search_server_action(action_id)
						#print "[E2VDOM] Action", action
						if action is None:
							target="\"ACHTUNG! UNKNOWN ACTION %s\""%(action_id)
						else:
							target="\"server\""
							#if action.target_object in container.object.objects:
							#	target="\"server\""
							#else:
							#	target="\"Object_%s:bubbleEvent(\"%s\")\""%(container.id.replace("-", "_"), self.name)
							#	# schedule dispatch
					else:
						#if action.target_object in container.object.objects:
						target="\"Obj_%s:%s(%s)\"" % ( action.target_object.replace("-", "_"), action.method_name,
							#", ".join([parameter.value.replace('"',r'\"') for parameter in action.parameters]) )
							compile_registations_render_params(action.parameters) )
						#print compile_registations_render_params(action.parameters)
						#else:
						#	target="\'Obj_%s:bubbleEvent(\"%s\")\'"%(container.id.replace("-", "_"), action.method_name)
					lines.append(
						"Obj_%(container)s_Dispatcher.addDispatchEvent(%(source)s, %(target)s);"%\
						{"container": container.id.replace("-", "_"), "source": source, "target": target})
					#print "Obj_%(container)s_Dispatcher.addDispatchEvent(%(source)s, %(target)s);"%\
					#	{"container": container.id.replace("-", "_"), "source": source, "target": target}


	for object in container.object.get_objects_list():
		lines.append(
			"Obj_%(object)s=new VDOM_Type_%(object_type)s(\"o_%(object)s\", Obj_%(container)s_EventEngine);"%\
			{"container": container.id.replace("-", "_"),
			"object": object.id.replace("-", "_"), "object_type": object.type.id.replace("-", "_")})

	#print "[E2VDOM] Container %s, parent %s"%(container.id, parent)
	#lines.append(
	#	"Obj_%(container)s=new VDOM_Obj_Type_%(type)s(\"o_%(container)s\", Obj_%(container)s_EventEngine);"%\
	#	{"container": container.id.replace("-", "_"), "type": container.object.type.id.replace("-", "_")})
	lines.append( # Leo
		"Obj_%(container)s=new VDOM_Type_%(type)s(\"o_%(container)s\", Obj_%(container)s_EventEngine);"%\
		{"container": container.id.replace("-", "_"), "type": container.object.type.id.replace("-", "_")})
	if parent:
		lines.append(
			"Obj_%(container)s.bubbleEvent=function(e){"\
			"Obj_%(container)s.riseEvent('tfrEvent', e.parameters, Obj_%(parent)s_eventEngine);};"%\
			{"container": container.id.replace("-", "_"), "parent": parent.replace("-", "_")})
	lines.append(
		"Obj_%(container)s_EventEngine.start();"%\
		{"container": container.id.replace("-", "_")})

	#lines.append("});")

	return "\n".join(lines)
