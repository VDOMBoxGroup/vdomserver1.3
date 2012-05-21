
import sys, traceback, os, socket, select, gc, re, resource, collections
from utils.threads import VDOM_thread
from utils.tracing import get_thread_trace, get_threads_trace


def ping(match):
	"""<action\s+name=(?P<quote1>['"])ping(?P=quote1)\s*(?:/>|>\s*</action>)"""
	return "<reply/>"

def state(match):
	"""<action\s+name=(?P<quote1>['"])state(?P=quote1)\s*""" \
	"""(?:/>|>\s*(?:<option\s+name=(?P<quote2>['"])thread(?P=quote2)\s*>\s*(?P<thread>-?\d+)\s*</option>\s*)?</action>)"""
	if match.group("thread"):
		try:
			thread, smart, stack=get_thread_trace(int(match.group("thread")))
		except:
			return "<error>no thread</error>"
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

def analyse(match):
	"""<action\s+name=(?P<quote1>['"])analyse(?P=quote1)\s*>\s*<option\s+name=(?P<quote2>['"])""" \
	"""(?P<option>objects|garbage|(?P<is_tracking>tracking))(?P=quote2)\s*"""\
	"""(?(is_tracking)(?:/>|>\s*</option>|>\s*(?P<tracking>enable|disable)\s*</option>)|""" \
	"""(?:/>|>\s*</option>))\s*</action>"""
	option=match.group("option")
	if option=="objects":
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
	elif option=="garbage":
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
	elif option=="tracking":
		value=match.group("tracking")
		if value=="enable":
			pass
		elif value=="disable":
			pass
		else:
			pass


class VDOM_watcher_session(VDOM_thread):

	pattern=re.compile("""\s*<action\s+name=(?P<quote1>['"])(?P<name>[A-Za-z][0-9A-Za-z]*)(?P=quote1)""")
	routines={routine.__name__: (routine, re.compile("\s*%s"%routine.__doc__)) for routine in (ping, state, analyse)}

	def __init__(self, connection):
		VDOM_thread.__init__(self, name="Watcher %s:%d"%connection.getpeername())
		self._connection=connection

	def main(self):
		print "Watcher: Start session with %s:%d"%self._connection.getpeername()
		message, pattern="", None
		while self.running:
			reading, writing, erratic=select.select((self._connection,), (), (), self.quantum)
			if reading:
				chunk=self._connection.recv(4096)
				if not chunk:
					break
				message+=chunk
				while True:
					if not pattern:
						match=self.pattern.match(message)
						if match:
							routine, pattern=self.routines[match.group("name")]
						else:
							break
					match=pattern.match(message)
					if match:
						try:
							response=routine(match)
						except:
							response="<error>internal error</error>"
							traceback.print_exc()
						self._connection.send(response)
						message, pattern=message[match.end():], None
					else:
						break
		print "Watcher: End session with %s:%d"%self._connection.getpeername()
		self._connection.close()

class VDOM_watcher(VDOM_thread):

	pattern=re.compile("""\s*<action\s+name=(?P<quote1>['"])(?P<name>[A-Za-z][0-9A-Za-z]*)(?P=quote1)""")
	routines={routine.__name__: (routine, re.compile("\s*%s\s*$"%routine.__doc__)) for routine in (ping, state, analyse)}

	def __init__(self):
		VDOM_thread.__init__(self, name="Watcher")
		self._address=VDOM_CONFIG["SERVER-ADDRESS"]
		self._port=VDOM_CONFIG["WATCHER-PORT"]
		self._socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._socket.bind((self._address, self._port))
		self._session_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._session_socket.bind((self._address, self._port))
		self._session_socket.listen(5)

	def main(self):
		while self.running:
			reading, writing, erratic=select.select((self._socket, self._session_socket), (), (), self.quantum)
			if self._socket in reading:
				try:
					message, address=self._socket.recvfrom(512)
					print "Watcher: Receive request from %s:%d"%address
					match=self.pattern.match(message)
					try:
						routine, pattern=self.routines[match.group("name")]
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
					print "Watcher: Receive response to %s:%d"%address
					try:
						shift = -1
						for shift in xrange(0, len(response) / 8000):
							self._socket.sendto(response[shift*8000:(shift+1)*8000], address)
						self._socket.sendto(response[(shift+1)*8000:], address)
					except socket.error:
						print "Watcher: Unable to send response"
			if self._session_socket in reading:
				connection, address=self._session_socket.accept()
				VDOM_watcher_session(connection).start()
