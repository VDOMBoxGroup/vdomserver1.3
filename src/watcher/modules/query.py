
import sys, gc, collections
from ..auxiliary import select_objects, generate_graph


def query(options):
	print "QUERY", options
	if "objects" in options:
		objects=select_objects(options["objects"])
		yield "<reply>"
		yield "<objects>"
		for object in objects:
			yield "<object id=\"%08X\"/>"%id(object)
		yield "</objects>"
		yield "</reply>"
	elif "garbage" in options:
		objects=gc.garbage
		yield "<reply>"
		yield "<objects>"
		for object in objects:
			yield "<object id=\"%08X\"/>"%id(object)
		yield "</objects>"
		yield "</reply>"
	elif "referrers" in options:
		objects=select_objects(options["referrers"])
		ignore=set((id(sys._getframe()), id(objects)))
		referrers=gc.get_referrers(*objects)
		yield "<reply>"
		yield "<referrers>"
		for referrer in referrers:
			if id(referrer) in ignore: continue
			yield "<referrer id=\"%08X\"/>"%id(referrer)
		yield "</referrers>"
		yield "</reply>"
	elif "referents" in options:
		objects=select_objects(options["referents"])
		ignore=set((id(sys._getframe()), id(objects)))
		referents=gc.get_referents(*objects)
		yield "<reply>"
		yield "<referents>"
		for referent in referents:
			if id(referent) in ignore: continue
			yield "<referent id=\"%08X\"/>"%id(referent)
		yield "</referents>"
		yield "</reply>"
	elif "graph" in options:
		print "!!!!!!!!!!!!!!!!!!!!!"
		objects=select_objects(options["graph"])
		print ">>>", objects
		yield "<reply>"
		yield "<graph>"
		yield "".join(generate_graph(objects)).encode("xml")
		yield "</graph>"
		yield "</reply>"
		print "DONE!!!!!!!!!!!"
