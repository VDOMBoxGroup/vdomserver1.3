"""resource module"""
import sys
import managers
from module import VDOM_module
from utils.exception import *


class VDOM_module_resource(VDOM_module):
	"""resource module class"""

	content_type = {
		"bmp"	:	"image/bmp",
		"jpg"	:	"image/jpeg",
		"jpeg"	:	"image/jpeg",
		"png"	:	"image/png",
		"gif"	:	"image/gif",
		"css"	:	"text/css",
		"htm"	:	"text/html",
		"html"	:	"text/html",
		"swf"	:	"application/x-shockwave-flash",
		"xml"	:	"text/xml",
		"res"	:	"resource",
		"pdf"	:	"application/pdf",
		"mid"	:	"audio/midi",
		"js"	:	"text/javascript",
		"wav"	:	"audio/wav",
		"doc"	:	"application/msword",
		"dot"	:	"application/msword",
		"xls"	:	"application/msexcel",
	        "htc"	:	"text/x-component",
		"unknown"	:	"application/octet-stream"
	}

	images = ["bmp", "jpg", "jpeg", "png", "gif"]

	def getfile(self, application_id, file):
		""" read file """
		self.content = ""
		self.fd = None
		self.ctype = ""
		filename = ""
		if file[0] == "/":
			filename = file[1:]
		else:
			filename = file
		try:
			resource = managers.resource_manager.get_resource(application_id, filename.split(".")[0])
			if not resource:
				raise VDOM_exception("Resource not found")
			self.fd = resource.get_fd()
			self.extension = resource.res_format.lower()
			self.downloadname = resource.name
			if self.extension not in VDOM_module_resource.content_type:
				self.ctype = "unknown"
			else:
				self.ctype = self.extension
			return resource
		except:
			debug("Error reading resource %s:%s" % (str(application_id), str(file)))
			return None

	def run(self, request_object, request_type):
		"""process request"""
		request_uri = request_object.environment().environment()["REQUEST_URI"]
		application_id = request_object.app_id()
		ro = self.getfile(application_id, request_uri)
		if not self.ctype:
			return None

		if ro and ro.label is not "":
			request_object.add_header("Cache-Control", "no-cache")
		elif ro and ro.label is "" and self.ctype in VDOM_module_resource.images + ["css","js"]:
			request_object.add_header("Cache-Control", "max-age=86400")

		request_object.add_header("Content-Type", VDOM_module_resource.content_type[self.ctype])
		if self.ctype == "unknown" or self.ctype in ("doc","dot","xls"):
			if self.extension =="":
				ext = "."+self.extension
			else:
				ext = self.extension
			request_object.add_header("Content-Disposition", "attachment; filename=\"%s.%s\""%(self.downloadname.encode("utf-8"), ext))

		return self.fd
