
import gc, collections


def analyse(options):
	if "objects" in options:
		reference=collections.defaultdict(int)
		for item in gc.get_objects():
			reference[type(item)]+=1
		counters="".join((
			"<counter object=\"%s\">%d</counter>"% \
				(item.__name__ if item.__module__=="__builtin__" else "%s.%s"%(item.__module__, item.__name__), counter) \
					for item, counter in reference.iteritems()))
		return \
			"<reply>" \
				"<counters>" \
					"%s" \
				"</counters>" \
			"</reply>"%(counters)
	elif "garbage" in options:
		reference=collections.defaultdict(int)
		for item in gc.garbage:
			reference[type(item)]+=1
		counters="".join((
			"<counters object=\"%s\">%d</counters>"% \
				(item.__name__ if item.__module__=="__builtin__" else "%s.%s"%(item.__module__, item.__name__), counter) \
					for item, counter in reference.iteritems()))
		return \
			"<reply>" \
				"<counters>" \
					"%s" \
				"</counters>" \
			"</reply>"%(counters)
