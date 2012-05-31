
import gc, collections


def analyse(options):
	if "objects" in options:
		reference=collections.defaultdict(int)
		for item in gc.get_objects(): reference[type(item)]+=1
		yield "<reply>"
		yield "<counters>"
		for item, counter in reference.iteritems():
			name=item.__name__ if item.__module__=="__builtin__" else "%s.%s"%(item.__module__, item.__name__)
			yield "<counter object=\"%s\">%d</counter>"% \
				(name.encode("xml"), counter)
		yield "</counters>"
		yield "</reply>"
	elif "garbage" in options:
		reference=collections.defaultdict(int)
		for item in gc.garbage: reference[type(item)]+=1
		yield "<reply>"
		yield "<counters>"
		for item, counter in reference.iteritems():
			name=item.__name__ if item.__module__=="__builtin__" else "%s.%s"%(item.__module__, item.__name__)
			yield "<counter object=\"%s\">%d</counter>"% \
				(name.encode("xml"), counter)
		yield "</counters>"
		yield "</reply>"
