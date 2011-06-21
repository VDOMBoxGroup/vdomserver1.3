
import re, managers


class VDOM_objects(object):
	
	guid_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)
	
	def create(self, type, parent, name=None):
		application=managers.request_manager.get_request().application()
		if not VDOM_objects.guid_regex.search(type):
			xml_type=managers.xml_manager.get_type_by_name(type)
			type=xml_type.id if xml_type is not None else None
		if VDOM_objects.guid_regex.search(parent):
			parent=application.search_object(parent)
		else:
			objects=application.search_objects_by_name(parent)
			parent=objects[0] if len(objects)==1 else None
		if type is None or parent is None: return None
		object_tuple=application.create_object(type, parent)
		object=application.search_object(object_tuple[1])
		if name is not None: object.set_name(name)
		return object

	def delete(self, object_string):
		application=managers.request_manager.get_request().application()
		if VDOM_objects.guid_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if len(objects)==1 else None
		if object is None: return
		application.delete_object(object)

	def search(self, object_string):
		application=managers.request_manager.get_request().application()
		if VDOM_objects.guid_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if objects else None
		return object

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
		self._objects=VDOM_objects()
		self._databases=VDOM_databases()
		self._resources=VDOM_resources()
		self._storage=VDOM_storage()

	def _get_id(self):
		return managers.request_manager.current.app_id()

	def _get_name(self):
		return managers.request_manager.current.application().name
	
	id=property(_get_id)
	name=property(_get_name)
	objects=property(lambda self: self._objects)
	databases=property(lambda self: self._databases)
	resources=property(lambda self: self._resources)
	storage=property(lambda self: self._storage)
