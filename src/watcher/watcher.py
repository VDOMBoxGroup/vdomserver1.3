
import sys, socket, select, gc
from utils.threads import VDOM_thread
from utils.tracing import get_threads_trace

class VDOM_watcher(VDOM_thread):

	def __init__(self):
		VDOM_thread.__init__(self, name="Observer")
		self._address=VDOM_CONFIG["SERVER-ADDRESS"]
		self._port=VDOM_CONFIG["WATCHER-PORT"]
		self._socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._socket.bind((self._address, self._port))
		self._allowable={"ping": self.ping, "state": self.state}

	def main(self):
		while self.running:
			reading, writing, erratic=select.select((self._socket,), (), (), self.quantum)
			if reading:
				try:
					message, address=self._socket.recvfrom(512)
					option=message[1:message.index(">", 1)]
					self._socket.sendto(self._allowable[option.rstrip("/ \t")](address, message), address)
				except (ValueError, KeyError):
					self._socket.sendto("<error>incorrect request</error>", address)
				except socket.error:
					pass

	def ping(self, address, message):
		return "<ping/>"

	def state(self, address, message):
		threads="".join(
			("\t\t<thread>\n" \
			"\t\t\t<name>%s</name>\n" \
			"\t\t\t<id>%d</id>\n" \
			"\t\t\t<daemon>%s</daemon>\n" \
			"\t\t\t<smart>%s</smart>\n" \
			"\t\t\t<stack>\n" \
			"%s" \
			"\t\t\t</stack>\n" \
			"\t\t</thread>\n"%(thread.name.encode("xml"), thread.ident, "yes" if thread.daemon else "no", "yes" if smart else "no", "".join(
				("\t\t\t\t<line>\n" \
				"\t\t\t\t\t<path>%s</path>\n" \
				"\t\t\t\t\t<line>%s</line>\n" \
				"\t\t\t\t\t<function>%s</function>\n" \
				"\t\t\t\t\t<statement>%s</statement>\n" \
				"\t\t\t\t</line>\n"%(path.encode("xml"), line, function.encode("xml"), statement.encode("xml")) \
				for path, line, function, statement in stack))) \
			for thread, smart, stack in get_threads_trace()))
		state="enabled" if gc.isenabled() else "disabled"
		counter0, counter1, counter2=gc.get_count()
		return \
			"<state>\n" \
			"\t<threads>\n" \
			"%(threads)s" \
			"\t</threads>\n" \
			"\t<garbagecollector>\n" \
			"\t\t<state>%(state)s</state>\n" \
			"\t\t<counters>\n" \
			"\t\t\t<generation0>%(counter0)d</generation0>\n" \
			"\t\t\t<generation1>%(counter1)d</generation1>\n" \
			"\t\t\t<generation2>%(counter2)d</generation2>\n" \
			"\t\t</counters>\n" \
			"\t</garbagecollector>\n" \
			"</state>\n"%locals()
