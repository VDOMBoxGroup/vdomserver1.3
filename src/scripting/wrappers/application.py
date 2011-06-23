
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
	
	def create(self, data, resource_format="res", name=""):
		"""Create new resource"""
		application_id=managers.request_manager.current.app_id()
		attributes = {"res_type":"permanent",
						"res_format":resource_format,
						"name":name,
		
						}
		managers.resource_manager.add_resource(application_id, None, attributes, data)
		#application.create_resource(application.id, as_string(type), as_string(name), as_binary(data))
		return id
		
	def delete(self, resource_id):
		"""Delete resource"""
		application_id=managers.request_manager.current.app_id()
		managers.resource_manager.delete_resource(application_id, resource_id)

	def create_temporary(self, object_id, label, data, resource_format="res", name=""):
		"""Create temporary resource with lable"""
		application_id=managers.request_manager.current.app_id()
		
		attributes = {"res_type":"temporary",
					  "res_format":resource_format,
					  "name":name,
					  "label":label,
					 }
		
		managers.resource_manager.add_resource(application_id, object_id, attributes, data)

	def get(self, res_id):
		"""Geting resource"""
		application_id=managers.request_manager.current.app_id()
		managers.resource_manager.get_resource(application_id, res_id)
		
	def get_list(self):
		"""Geting resource list"""
		application_id=managers.request_manager.current.app_id()
		managers.resource_manager.list_resource(application_id)		
		
	def get_by_label(self, object_id, label):
		managers.resource_manager.get_resource_by_label(object_id, label)	
		
	
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
		
	def _get_structure(self):
		return managers.request_manager.current.application().app_map
	
	id=property(_get_id)
	name=property(_get_name)
	structure=property(_get_structure)
	objects=property(lambda self: self._objects)
	databases=property(lambda self: self._databases)
	resources=property(lambda self: self._resources)
	storage=property(lambda self: self._storage)
