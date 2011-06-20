
import managers


class VDOM_storage(object):
	
	pass

class VDOM_databases(object):
	
	pass

class VDOM_resources(object):
	
	def create(self, type, name, data):
		application=managers.request_manager.get_request().application()
		id=unicode(utils.uuid.uuid4())
		application.create_resource(id, as_string(type), as_string(name), as_binary(data))
		return id
		
	def delete(self, resource):
		application=managers.request_manager.get_request().application()
		managers.resource_manager.delete_resource(application, resource)

class VDOM_application(object):
	
	def __init__(self):
		self._databases=VDOM_databases()
		self._resources=VDOM_resources()
		self._storage=VDOM_storage()

	def _get_id(self):
		return managers.request_manager.current.app_id()

	def _get_name(self):
		return managers.request_manager.current.application().name
	
	id=property(_get_id)
	name=property(_get_name)
	objects=property(lambda self: None)
	databases=property(lambda self: self._databases)
	resources=property(lambda self: self._resources)
	storage=property(lambda self: self._storage)
