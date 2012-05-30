
import sys, gc, collections
from ..auxiliary import select_objects, generate_graph


def query(options):
	if "objects" in options:
		objects=select_objects(options["objects"])
		yield "<reply>"
		yield "<objects>"
		for object in objects:
			yield "<object id=\"%08X\"/>"%id(object)
		yield "</objects>"
		yield "</reply>"
	elif "referrers" in options:
		objects=select_objects(options["referrers"])
		referrers=gc.get_referrers(object)
		ignore=set((id(sys._getframe()), id(objects)), id(referrers))
		yield "<reply>"
		yield "<referrers>"
		for referrer in referrers:
			if id(referrer) in ignore: continue
			yield "<referrer id=\"%08X\"/>"%id(referrer)
		yield "</referrers>"
		yield "</reply>"
	elif "referents" in options:
		objects=select_objects(options["referents"])
		referents=gc.get_referents(object)
		ignore=set((id(sys._getframe()), id(objects)), id(referents))
		yield "<reply>"
		yield "<referents>"
		for referent in referents:
			if id(referent) in ignore: continue
			yield "<referent id=\"%08X\"/>"%id(referent)
		yield "</referents>"
		yield "</reply>"
	elif "graph" in options:
		objects=select_objects(options["graph"])
		yield "<reply>"
		yield "<graph>"
		yield "".join(generate_graph(objects)).encode("xml")
		yield "</graph>"
		yield "</reply>"
