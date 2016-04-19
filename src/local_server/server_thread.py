
import sys, os, thread, socket, select,traceback

from version import VDOM_server_version
from utils.threads import VDOM_thread
import local_server


class VDOM_local_server_thread(VDOM_thread):

	def __init__(self):
		VDOM_thread.__init__(self, name="Local Server")
		port=VDOM_CONFIG["SERVER-LOCALHOST-PORT"]
		if port == 0:
			self.stop()
			return
		self.__local_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.__local_socket.bind(('localhost', port))
		local_server.send_to_card("online")
		sys.stderr.write("Listening on localhost: %d\n"%port)
			

	def handle_specific_request(self, command):
		try:
			local_server.execute(command)
		except:
			traceback.print_exc(file=debugfile)

	def main(self):
		sys.stderr.write("Start %s\n"%self.name)
		while self.running:
			ret = select.select([self.__local_socket], [], [], self.quantum)
			for r in ret[0]:
				if r == self.__local_socket:
					(string, address) = self.__local_socket.recvfrom(102400)
					if "stop" == string:
						#self.__stop = True
						debug("Stop from %s - ignore\n"%address[0])
						#raise socket.error("")
					elif "restart" == string:
						#self.restart = True
						#self.__stop = True
						debug("Restart from %s - ignore\n"%address[0])
						#raise socket.error("")
					else:
						# create thread to handle specific request from localhost
						thread.start_new_thread(self.handle_specific_request, (string, ))

	def stop(self):
		sys.stderr.write("Stop %s\n"%self.name)
		super(VDOM_local_server_thread, self).stop()
