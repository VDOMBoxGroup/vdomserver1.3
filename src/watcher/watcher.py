
import sys, traceback, os, socket, select, gc, re, resource
from utils.threads import VDOM_thread
from utils.tracing import get_thread_trace, get_threads_trace


class VDOM_watcher(VDOM_thread):

	main_pattern=re.compile("""\s*<(?P<name>[A-Za-z][0-9A-Za-z]*)""")
	ping_pattern=re.compile("""\s*<ping(?:\s*/>|\s*>\s*</ping>\s*)$""")
	state_pattern=re.compile("""\s*<state(?:\s+thread="(?P<thread>\d+)")?(?:\s*/>|\s*>\s*</state>\s*)$""")

	def __init__(self):
		VDOM_thread.__init__(self, name="Watcher")
		self._address=VDOM_CONFIG["SERVER-ADDRESS"]
		self._port=VDOM_CONFIG["WATCHER-PORT"]
		self._socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._socket.bind((self._address, self._port))
		self._allowable={
			"ping": (self.ping, self.ping_pattern),
			"state": (self.state, self.state_pattern)}

	def main(self):
		while self.running:
			reading, writing, erratic=select.select((self._socket,), (), (), self.quantum)
			if reading:
				try:
					message, address=self._socket.recvfrom(512)
					match=self.main_pattern.match(message)
					try:
						routine, pattern=self._allowable[match.group("name")]
						match=pattern.match(message)
						if not match: raise ValueError
						try:
							response=routine(match)
						except:
							response="<error>internal error</error>"
							traceback.print_exc()
					except:
						response="<error>incorrect request</error>"
				except socket.error:
					response=None
				if response:
					try:
						self._socket.sendto(response, address)
					except socket.error:
						pass

	def ping(self, match):
		return "<ping/>"

	def state(self, match):
		if match.group("thread"):
			data=get_thread_trace(int(match.group("thread")))
			if not data:
				return "<error>no thread</error>"
			thread, smart, stack=data
			frames="".join((
				"<frame>" \
					"<path>%s</path>" \
					"<line>%s</line>" \
					"<function>%s</function>" \
				"</frame>"%(path.encode("xml"), line, function.encode("xml")) for path, line, function, statement in stack))
			return \
				"<state>" \
					"<thread id=\"%s\"%s%s>" \
						"<name>%s</name>" \
						"<stack>%s</stack>" \
					"</thread>" \
				"</state>"%(thread.ident,
					" daemon=\"yes\"" if thread.daemon else "",
					" smart=\"yes\"" if smart else "",
					thread.name.encode("xml"), frames)
		else:
			try:
				usage=resource.getrusage(resource.RUSAGE_SELF)
				process= \
					"<process id=\"%d\">" \
						"<usage>" \
							"<utime>%.3f</utime>" \
							"<stime>%.3f</stime>" \
							"<maxrss>%d</maxrss>" \
							"<ixrss>%d</ixrss>" \
							"<idrss>%d</idrss>" \
						"</usage>" \
					"</process>"%(os.getpid(), usage.ru_utime, usage.ru_stime, usage.ru_maxrss, usage.ru_ixrss, usage.ru_idrss)
			except:
				process="<process id=\"%d\"/>"%os.getpid()
			threads="".join((
				"<thread id=\"%s\">%s</thread>"%(thread.ident, thread.name.encode("xml")) for thread, smart, stack in get_threads_trace()))
			counter0, counter1, counter2=gc.get_count()
			return \
				"<state>" \
					"%s" \
					"<threads>%s</threads>" \
					"<garbagecollector%s>" \
						"<counters>" \
							"<counter generation=\"0\">%d</counter>" \
							"<counter generation=\"1\">%d</counter>" \
							"<counter generation=\"2\">%d</counter>" \
						"</counters>" \
						"<garbage number=\"%d\"/>" \
						"<objects number=\"%d\"/>" \
					"</garbagecollector>" \
				"</state>"%(process, threads,
					"" if gc.isenabled() else " state=\"disabled\"",
					counter0, counter1, counter2, len(gc.garbage), len(gc.get_objects()))
