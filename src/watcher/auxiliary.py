
import sys, types, numbers, gc, inspect, re, traceback
from utils.tracing import normalize_source_path
#from collections import defaultdict


# LATEST IN GRAPH

def quote(s):
	return (s.replace("\\", "\\\\")
		.replace("\"", "\\\"")
		.replace("\n", "\\n")
		.replace("\0", "\\\\0"))

def make_graph(objects, optimize=True, collapse_dicts=True, skip_functions=True):
	# TODO: __del__
	# TODO: Dereference members

	def check_dicts(target):
		if not collapse_dicts: return None
		if not isinstance(target, dict): return None
		if id(target) in dicts: return dicts[id(target)]

		ignore.add(id(sys._getframe()))

		sources=gc.get_referrers(target)
		ignore.add(id(sources))
		try:
			master=None
			for source in sources:
				if id(source) in ignore: continue
				if skip_functions \
					and isinstance(source, types.FunctionType) \
					and source.__globals__ is target: continue
				source_dict=getattr(source, "__dict__", None)
				if isinstance(source_dict, types.DictProxyType):
					source_dict=gc.get_referents(gc.get_referents(source_dict))[0]
				if target is source_dict:
					if master:
						dicts[id(target)]=None
						return None
					else:
						master=source
				"""
				else:
					dicts[id(target)]=None
					return None
				"""
				del source
			if master:
				dicts[id(target)]=master
				return master
			else:
				return None
		finally:
			ignore.remove(id(sources))
			del sources

	def show_edge(source, target):
		if collapse_dicts and id(source) in dicts:
			for key, value in source.iteritems():
				if value is target:
					membership_edges.append((id(dicts[id(source)]), mapping.get(id(target), id(target)), quote(key)))
					return

		if mapping.get(id(target), None)==id(source):
			return

		if isinstance(target, dict):
			source_dict=getattr(source, "__dict__", None)
			if isinstance(source_dict, types.DictProxyType):
				source_dict=gc.get_referents(gc.get_referents(source_dict))[0]
			if target is source_dict:
				elementary_edges.append((id(source), mapping.get(id(target), id(target)), "__dict__"))
				return
		if isinstance(source, type):
			if target in source.__bases__:
				inheritance_edges.append((id(source), mapping.get(id(target), id(target)), ""))
				return

		if getattr(source, "__class__", None) is target:
			instance_edges.append((id(source), mapping.get(id(target), id(target)), ""))
			return
		elif getattr(source, "__self__", None) is target:
			ownership_edges.append((id(source), mapping.get(id(target), id(target)), ""))
			return
		elif isinstance(source, dict):
			for key, value in source.iteritems():
				if value is target:
					elementary_edges.append((id(source), mapping.get(id(target), id(target)), quote(repr(key))))
			return
		elif isinstance(source, types.FrameType) and source.f_back is target:
			traceback_edges.append((id(source), mapping.get(id(target), id(target)), ""))
			return

		try:
			if target in source:
				elementary_edges.append((id(source), mapping.get(id(target), id(target)), ""))
				return
		except:
			pass

		for name in dir(source):
			try:
				if target is getattr(source, name):
					elementary_edges.append((id(source), mapping.get(id(target), id(target)), name))
					return
			except:
				pass

		reference_edges.append((id(source), mapping.get(id(target), id(target)), ""))

	def show_node(target):
		kind=type(target).__name__
		if isinstance(target, type):
			name=target.__name__
			module=target.__module__
			storage=inheritance_nodes
		elif isinstance(target, types.ModuleType):			
			name=target.__name__
			module=" " # target.__package__
			storage=module_nodes
		elif isinstance(target, (types.BuiltinMethodType, types.BuiltinFunctionType)):
			name=target.__name__
			module=" "
			storage=elementary_nodes
		elif isinstance(target, types.FunctionType):
			name=target.__name__
			module=getattr(inspect.getmodule(target), "__name__", " ")
			storage=callable_nodes
		elif isinstance(target, types.CodeType):
			name=target.co_name
			module=getattr(inspect.getmodule(target), "__name__", " ")
			storage=callable_nodes
		elif isinstance(target, types.MethodType):
			if target.__self__ is not None: kind="bound "+kind
			name=target.__func__.__name__
			module=getattr(inspect.getmodule(target), "__name__", " ")
			storage=callable_nodes
		elif isinstance(target, types.FrameType):
			name=target.f_code.co_name # normalize_source_path(target.f_code.co_filename), target.f_lineno
			module=getattr(inspect.getmodule(target), "__name__", " ")
			storage=callable_nodes
		elif isinstance(target, types.InstanceType):
			name=target.__class__.__name__
			module=target.__module__
			storage=elementary_nodes
		elif type(target).__module__=="__builtin__":
			name=quote(repr(target))[:40] if isinstance(target, (basestring, numbers.Number, bool)) else " "
			module=" "
			storage=elementary_nodes
		else:
			kind="object"
			name=type(target).__name__
			module=type(target).__module__
			storage=object_nodes
		if target in objects: storage=primary_nodes
		storage.append((id(target), quote("\n".join((kind, name, module, "%08X"%id(target))))))

	primary_nodes=[]
	inheritance_nodes=[]
	callable_nodes=[]
	module_nodes=[]
	elementary_nodes=[]
	object_nodes=[]

	membership_edges=[]
	callable_edges=[]
	traceback_edges=[]
	reference_edges=[]
	ownership_edges=[]
	instance_edges=[]
	inheritance_edges=[]
	elementary_edges=[]

	queue, levels, ignore, mapping, dicts=[], {}, set(), {}, {}

	ignore.add(id(objects))
	ignore.add(id(sys._getframe()))
	ignore.add(id(queue))
	ignore.add(id(dicts))

	for target in objects:
		check_dicts(target)
		levels[id(target)]=0
		queue.append(target)

	gc.collect()
	while queue:
		target=queue.pop(0)
		level=levels[id(target)]
		
		if collapse_dicts and id(target) in dicts:
			mapping[id(target)]=id(dicts[id(target)])
		else:
			show_node(target)

		#if level>5: continue
		if isinstance(target, types.ModuleType): continue
		if isinstance(target, (basestring, numbers.Number, bool)): continue

		sources=gc.get_referrers(target)
		ignore.add(id(sources))
		for source in sources:
			if id(source) in ignore: continue
			if skip_functions \
				and isinstance(source, types.FunctionType) \
				and source.__globals__ is target: continue
			check_dicts(source)
			if id(source) not in levels:
				levels[id(source)]=level+1
				queue.append(source)
			show_edge(source, target)
		ignore.remove(id(sources))
		sources=None

	# D69191 A06C6C		Light Red			Unknown References
	# DEB887 A68A65		Light Brown			Objects, Membership
	# CCC0A8			Light Light Brown
	# D497E3 9F71AA		Light Magenta		Inheritance
	# D8D8D8 A2A2A2		Light Gray			Elementary Objects, Elementary References
	# 57A77A			Ocean Green
	# 65B488			Light Green			Primary Objects
	# 76A3C9			Light Blue			Callable Objects
	# DECD87			Light Yellow		Modules
	# CDC9A5			Light Light Yellow
	# 87D5DE			Light Blue

	yield "digraph ObjectGraph\n" \
		"{\n" \
		"\tpack=true;\n" \
		"\toverlap=false;\n" \
		"\toutputorder=nodesfirst;\n" \
		"\tbgcolor=\"#FFFFFF\";\n" \
		"\tnode[shape=rectangle, style=filled, penwidth=6, color=\"#FFFFFF\", fillcolor=\"#000000\", fontname=Consolas, fontsize=8]\n" \
		"\tedge[arrowsize=0.75, penwidth=2, color=\"#000000\", fontcolor=\"#000000\", fontname=Consolas, fontsize=8];\n"
	for storage, style in (
		(primary_nodes, 'fillcolor="#65B488"'),
		(inheritance_nodes, 'fillcolor="#D497E3"'),
		(callable_nodes, 'fillcolor="#76A3C9"'),
		(module_nodes, 'fillcolor="#DECD87"'),
		(elementary_nodes, 'fillcolor="#D8D8D8"'),
		(object_nodes, 'fillcolor="#DEB887"')):
		if not storage: continue
		yield "\tnode[%s];\n"%style
		for name, label in storage:
			yield "\t%s%s;\n"%(name, '[label="%s"]'%label if label else "")
	for storage, style in (
		(membership_edges, 'color="#DEB887", fontcolor="#A68A65", arrowhead=normal, weight=10'),
		(callable_edges, 'color="#DEB887", fontcolor="#A68A65", arrowhead=normal, weight=30'),
		(traceback_edges, 'color="#76A3C9", fontcolor="#A68A65", arrowhead=normal, weight=30'),
		(reference_edges, 'color="#D69191", fontcolor="#A06C6C", arrowhead=normal, weight=1'),
		(ownership_edges, 'color="#DEB887", fontcolor="#A68A65", arrowhead=empty, weight=1'),
		(instance_edges, 'color="#D497E3", fontcolor="#9F71AA", arrowhead=empty, weight=1'),
		(inheritance_edges, 'color="#D497E3", fontcolor="#9F71AA", arrowhead=normal, weight=1'),
		(elementary_edges, 'color="#D8D8D8", fontcolor="#A2A2A2", arrowhead=normal, weight=1')):
		if not storage: continue
		yield "\tedge[%s];\n"%style
		for name1, name2, label in storage:
			yield "\t%s->%s%s;\n"%(name1, name2, '[label=" %s"]'%label if label else "")
	yield "}\n"
	