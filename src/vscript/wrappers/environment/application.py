
import os
import managers
from file_access import storage
from utils.exception import VDOM_exception_file_access
from ... import errors
from ...subtypes import binary, generic, string, boolean, true, false, v_mismatch, v_nothing
from ...variables import variant


def normailze(filename):
	norm_name=os.path.normpath(filename)
	rel_path=os.path.relpath(os.path.abspath(managers.file_manager.get_path(storage,
		managers.request_manager.current.application_id, None, norm_name)),
		os.path.abspath(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"]))
	if rel_path[:36]!=managers.request_manager.current.application_id:
		raise VDOM_exception_file_access("Provided file name is invalid")
	return norm_name


class v_storage(generic):
	
	def v_exists(self, filename):
		try:
			return boolean(managers.file_manager.exists(storage,
				managers.request_manager.current.application_id, None,
				normailze(filename.as_string)))
		except IOError as exception:
			raise errors.system_error(exception.strerror)
	
	def v_delete(self, filename):
		try:
			managers.file_manager.delete(storage,
				managers.request_manager.current.application_id, None,
				normailze(filename.as_string))
		except IOError as exception:
			raise errors.system_error(exception.strerror)
		return v_mismatch

	def v_read(self, filename):
		try:
			content=managers.file_manager.read(storage,
				managers.request_manager.current.application_id, None,
				normailze(filename.as_string))
		except IOError as exception:
			raise errors.system_error(exception.strerror)
		try:
			return string(content.decode("utf-8"))
		except UnicodeDecodeError:
			return binary(content)

	def v_write(self, filename, content, asynchronous=None):
		try:
			content=content.as_string.encode("utf-8")
		except errors.type_mismatch:
			content=content.as_binary
		try:
			managers.file_manager.write(storage,
				managers.request_manager.current.application_id, None,
				normailze(filename.as_string), content,
				async=False if asynchronous is None else asynchronous.as_boolean)
		except IOError as exception:
			raise errors.system_error(exception.strerror)
		return v_mismatch


class v_application(generic):

	def __init__(self):
		self._storage=v_storage()

	def v_id(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("storage")
		else:
			return string(managers.request_manager.current.application().id)

	def v_name(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("storage")
		else:
			return string(managers.request_manager.current.application().name)

	def v_storage(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("storage")
		else:
			return self._storage
