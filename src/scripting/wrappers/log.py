
from datetime import datetime
import managers
import file_access


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class VDOM_log(object):

	def __init__(self):
		self._file=None

	def _open(self):
		self._file=managers.file_manager.get_fd(file_access.storage, "", None, "applications.log", "w")

	def _format(self, level, message, *arguments, **keywords):
		try:
			module=managers.request_manager.get_request().application().id
		except:
			module=""
		timestamp=datetime.now().strftime(TIMESTAMP_FORMAT)
		user=keywords.get("user", "")
		return "%s;%s;%s;%s;%s\n" % (timestamp, module, user, level, message % arguments)

	def write(self, message, *arguments, **keywords):
		message=self._format("", message, *arguments, **keywords)
		print message.encode("ascii", "backslashreplace"),
		if self._file is None:
			self._open()
		self._file.write(message.encode("utf8"))
		self._file.flush()

	def debug(self, message, *arguments, **keywords):
		message=self._format("debug", message, *arguments, **keywords)
		print message.encode("ascii", "backslashreplace"),
		if self._file is None:
			self._open()
		self._file.write(message.encode("utf8"))
		self._file.flush()

	def warning(self, message, *arguments, **keywords):
		message=self._format("warning", message, *arguments, **keywords)
		print message.encode("ascii", "backslashreplace"),
		if self._file is None:
			self._open()
		self._file.write(message.encode("utf8"))
		self._file.flush()

	def error(self, message, *arguments, **keywords):
		message=self._format("error", message, *arguments, **keywords)
		print message.encode("ascii", "backslashreplace"),
		if self._file is None:
			self._open()
		self._file.write(message.encode("utf8"))
		self._file.flush()
