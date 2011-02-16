
import shutil, os, os.path, sys, traceback, base64, zipfile, thread, time, copy, socket, select

from util.exception import *
from session_objects import *

class VDOM_memory_session():

	def __init__(self):
		self.sock = None
		self.__app = None

	def __del__(self):
		if self.sock:
			self.sock.send("close")
			self.sock.close()

	def create_request(self, method, param):	# param can be list of tuples or just dict
		ret = "<Method Name=\"" + method + "\">\n%s</Method>"
		par = ""
		_p = {}
		if isinstance(param, list):
			for item in param:
				_p[item[0]] = item[1]
		elif isinstance(param, dict):
			_p = param
		else:
			raise ValueError
		for item in _p:
			x = item
			y = _p[item]
			if y is None:
				y = ""
			if isinstance(x, unicode):
				x = x.encode("utf-8")
			if isinstance(y, unicode):
				y = y.encode("utf-8")
			par += "<Parameter Name=\"%s\"><![CDATA[%s]]></Parameter>\n" % (x, y.replace("]]>", "]]]]><![CDATA[>"))
		return ret % par

	def send_request(self, method, param):
		if not self.sock:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect(("localhost", VDOM_CONFIG["VDOM-MEMORY-SERVER-PORT"]))
		self.sock.send(self.create_request(method, param))
		return self.__get_response()

	def __get_response(self):
		resp = ""
		ret = select.select([self.sock], [], [])
		if len(ret[0]) > 0:
			while True:
				resp += self.sock.recv(4096)
				ret = select.select([self.sock], [], [], 0)
				if len(ret[0]) == 0:
					break
		if resp.startswith("<Error>"):
			raise VDOM_exception_vdommem(resp[7:-8])
		if resp.startswith("<Restart>"):
			raise VDOM_exception_restart()
		if "None" == resp:
			return None
		return resp

	# --- vdom memory ------------------------------------------------------

	def get_application(self, app_id, write = False):
		if self.__app:
			return self.__app
		self.appid = app_id
		if not self.appid:
			raise ValueError
		self.send_request("open_session", [("appid", self.appid), ("write", str(int(write)))])
		x = self.send_request("get_application", [("appid", self.appid)])
		if x:
			self.__app = VDOM_application_wrapper(self, data = x)
			return self.__app
		return None
