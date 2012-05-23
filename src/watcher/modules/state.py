
import os, gc, resource
from utils.tracing import get_thread_trace, get_threads_trace


def state(options):
	if "thread" in options:
		try:
			thread, smart, stack=get_thread_trace(int(options["thread"]))
		except:
			return "<reply><error>No thread</error></reply>"
		return \
			"<reply>" \
				"<thread name=\"%s\" id=\"%d\" daemon=\"%s\" smart=\"%s\">" \
					"<stack>%s</stack>" \
				"</thread>" \
			"</reply>"% \
				(thread.name.encode("xml"), thread.ident,
				"yes" if thread.daemon else "no", "yes" if smart else "no", "".join((
				"<frame name=\"%s\" path=\"%s\" line=\"%d\"/>"% \
					(name.encode("xml"), path.encode("xml"), line) for path, line, name, statement in stack)))
	else:
		try:
			usage=resource.getrusage(resource.RUSAGE_SELF)
			process= \
				"<process id=\"%d\">" \
					"<usage utime=\"%.3f\" stime=\"%.3f\" maxrss=\"%d\" idrss=\"%d\" ixrss=\"%d\"/>" \
				"</process>"% \
					(os.getpid(), usage.ru_utime, usage.ru_stime, usage.ru_maxrss, usage.ru_idrss, usage.ru_ixrss)
		except:
			process="<process id=\"%d\"/>"%os.getpid()
		count0, count1, count2=gc.get_count()
		return \
			"<reply>" \
				"%s" \
				"<threads>%s</threads>" \
				"<garbagecollector>" \
					"<objects>%d</objects>" \
					"<garbage>%d</garbage>" \
					"<collection>"\
						"<generation>%d</generation>" \
						"<generation>%d</generation>" \
						"<generation>%d</generation>" \
					"</collection>"\
				"</garbagecollector>" \
			"</reply>"% \
				(process, "".join(("<thread id=\"%s\" name=\"%s\"%s/>"% \
						(thread.ident, thread.name.encode("xml"), "" if thread.is_alive() else " alive=\"no\"") \
							for thread, smart, stack in get_threads_trace())),
					len(gc.get_objects()), len(gc.garbage), count0, count1, count2)
