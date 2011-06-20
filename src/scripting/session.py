
import managers


class VDOM_session(object):

	def _get_id(self):
		managers.request_manager.current.session().id()

	def __getitem__(self, name):
		return managers.request_manager.current.session()[name]

	def get(self, name, default=None):
		return managers.request_manager.current.session().get(name, default)

	def keys(self):
		return managers.request_manager.current.session().keys()

	def __iter__(self):
		return iter(managers.request_manager.current.session())

	id=property(_get_id)
