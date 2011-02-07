"""XML Manager module"""

import shutil, os, os.path, sys, traceback, base64, zipfile, thread, time, copy, socket, select

from src.xml.xml_object import xml_object
from src.util.semaphore import VDOM_semaphore
from src.util.exception import *
from session import VDOM_memory_session

class VDOM_memory_client(object):

	def new_session(self):
		return VDOM_memory_session()


internal_manager = VDOM_memory_client()
del VDOM_memory_client
