
import managers


class VDOM_headers(object):

	def __getitem__(self, name):
		return managers.request_manager.current.headers_out().headers()[name.lower()]

	def __setitem__(self, name, value):
		managers.request_manager.current.headers_out().headers()[name.lower()]=value

	def get(self, name, default=None):
		return managers.request_manager.current.headers_out().headers().get(name.lower(), default)

	def keys(self):
		return managers.request_manager.current.headers_out().headers().keys()

	def __contains__(self, name):
		return name.lower() in managers.request_manager.current.headers_out().headers()

	def __iter__(self):
		return iter(managers.request_manager.current.headers_out().headers())

class VDOM_response(object):
	
	def __init__(self):
		self._headers=VDOM_headers()

	def _get_cookies(self):
		return managers.request_manager.current.cookies()

	def _get_binary(self):
		return managers.request_manager.current.binary()

	def _set_binary(self, value):
		managers.request_manager.current.binary(b=value)

	def _set_nocache(self, value):
		if value: managers.request_manager.current.set_nocache()
	
	headers=property(lambda self: self._headers)
	cookies=property(_get_cookies)
	binary=property(_get_binary, _set_binary)
	nocache=property(fset=_set_nocache)

	def write(self, value, continue_render=False):
		if isinstance(value, basestring): managers.request_manager.current.write(value)
		elif hasattr(value, "read"): managers.request_manager.current.write_handler(value)
		else: raise ValueError
		if not continue_render: managers.engine.terminate()

	def send_file(self, filename, length, handler, content_type=None):
		return managers.request_manager.current.send_file(filename, length, handler, content_type)

	def redirect(self, target):
		managers.request_manager.current.redirect(target)
		managers.engine.terminate()

	def terminate(self):
		managers.engine.terminate()
