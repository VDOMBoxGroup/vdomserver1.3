
import sys, types, traceback, socket, select
from utils.threads import VDOM_thread
from utils.parsing import VDOM_parser
from utils.parsing.errors import VDOM_parsing_exception, VDOM_missing_attribute_error


import modules
modules={function.__name__: function for name, function in \
	((name, getattr(modules, name)) for name in dir(modules)) \
	if isinstance(function, types.FunctionType)}


def document_builder(parser):
	def document_handler(name, attributes):
		if name==u"session":
			# <session>
			def session_handler(name, attributes):
				if name==u"action":
					# <action>
					try: action_name=attributes.pop("name")
					except KeyError: raise VDOM_missing_attribute_error("Name")
					options={}
					def action_handler(name, attributes):
						if name==u"option":
							# <option>
							try: option_name=attributes.pop("name")
							except KeyError: raise VDOM_missing_attribute_error("Name")
							def option_handler(value): options[option_name]=value
							parser.handle_value_element(name, attributes, option_handler)
							# </option>
						else:
							parser.handle_unknown_element(name, attributes)
					def close_action_handler(name):
						parser.result.append((action_name, options))
					parser.handle_element(name, attributes, action_handler, close_action_handler)
					# </action>
				else:
					parser.handle_unknown_element(name, attributes)
			parser.handle_element(name, attributes, session_handler)
			# </session>
		else:
			parser.handle_unknown_element(name, attributes)
	return document_handler


class VDOM_watcher_session(VDOM_thread):

	def __init__(self, connection):
		VDOM_thread.__init__(self, name="Watcher Session %s"%connection.getpeername()[0])
		self._connection=connection

	def main(self):
		parser=VDOM_parser(builder=document_builder, result=[])
		parser.cache=True
		parser.parse(chunk="<session>")
		print "Watcher: Start session with %s"%self._connection.getpeername()[0]
		while self.running:
			try:
				reading, writing, erratic=select.select((self._connection,), (), (), self.quantum)
			except select.error:
				print "Watcher: Unable to check session state"
			else:
				if reading:
					try:
						message=self._connection.recv(4096)
					except socket.error as error:
						print "Watcher: Unable to receive request"
						break
					if not message: break
					try:
						parser.parse(chunk=message)
					except VDOM_parsing_exception:
						print "Watcher: Unable to parse request"
						try:
							self._connection.send("<reply><error>Incorrect request</error></reply>")
						except socket.error:
							print "Watcher: Unable to send response"
						break
					for name, options in parser.result:
						try:
							handler=modules[name]
						except KeyError:
							print "Watcher: Unable to find action"
							response="<reply><error>Incorrect request</error></reply>"
						else:
							try:
								response="".join(handler(options))
							except:
								print "Watcher: Unable to execute action"
								traceback.print_exc()
								response="<reply><error>Internal error</error></reply>"
						try:
							self._connection.send(response)
						except socket.error:
							print "Watcher: Unable to send response"
							break
					del parser.result[:]
		print "Watcher: Close session"
		self._connection.close()

class VDOM_watcher(VDOM_thread):

	def __init__(self):
		VDOM_thread.__init__(self, name="Watcher")
		self._address=VDOM_CONFIG["SERVER-ADDRESS"]
		self._port=VDOM_CONFIG["WATCHER-PORT"]
		self._socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._socket.bind((self._address, self._port))
		self._session_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._session_socket.bind((self._address, self._port))
		self._session_socket.listen(3)

	def main(self):
		parser=VDOM_parser(builder=document_builder, result=[])
		parser.cache=True
		print "Watcher: Start on %s:%d"%(self._address or "*", self._port)
		while self.running:
			try:
				reading, writing, erratic=select.select((self._socket, self._session_socket), (), (), self.quantum)
			except select.error:
				print "Watcher: Unable to check state"
			else:
				if self._socket in reading:
					try:
						message, address=self._socket.recvfrom(512)
					except socket.error:
						print "Watcher: Unable to receive request"
						continue
					print "Watcher: Receive session from %s"%address[0]
					try:
						parser.parse(chunk="<session>")
						parser.parse(chunk=message)
						parser.parse("</session>")
					except VDOM_parsing_exception as error:
						try:
							self._socket.sendto("<reply><error>Incorrect request</error></reply>", address)
						except socket.error:
							print "Watcher: Unable to send response"
					else:
						for name, options in parser.result:
							try:
								handler=modules[name]
							except KeyError:
								response="<reply><error>Incorrect request</error></reply>"
							else:
								try:
									response="".join(handler(options))
								except:
									print "Watcher: Unable to execute action"
									traceback.print_exc()
									response="<reply><error>Internal error</error></reply>"
							try:
								self._socket.sendto(response, address)
							except socket.error:
								print "Watcher: Unable to send response"
					parser.reset(result=[])
				if self._session_socket in reading:
					try:
						connection, address=self._session_socket.accept()
					except socket.error:
						print "Watcher: Unable to accept connection"
					VDOM_watcher_session(connection).start()
		print "Watcher: Shutdown"