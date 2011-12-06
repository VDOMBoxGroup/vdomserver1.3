
import hashlib
import managers
from utils.remote_api import VDOM_service
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *


class v_remoteserver(generic):
	
	def __init__(self, url, login, password, id):
		self.server=VDOM_service.connect(as_string(url), as_string(login),
			hashlib.md5(as_string(password)).hexdigest(), as_string(id))

	def __getattr__(self, name):
		def invoke(*arguments):
			self.server.remote(as_string(name), [as_string(argument) for argument in arguments], None)
		return invoke
