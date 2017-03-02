"""resource manager"""
import managers, file_access
from utils.exception import VDOM_exception
import utils.uuid
from resource.res_object import VDOM_resource_object, VDOM_resource_descriptor
import sys, copy
class VDOM_resource_manager(object):
	"""resource manager class"""

	def __init__(self):
		"""constructor"""
		#Old indexes
		self.__index = {}
		self.__label_index = {}
		self.save_index = True
		#NEW VERSION:
		self.__main_index = {}
		self.__name_index = {}

	def restore(self):	
		"""Restoring resources from last session.(After reboot or power off)"""
		self.__old_index = managers.storage.read_object(VDOM_CONFIG["RESOURCE-MANAGER-INDEX-STORAGE-RECORD"])

		already_exist = managers.storage.make_resources_index() # ?????

		if self.__old_index and not already_exist:
			#Transfering index to new format
			for resource in self.__old_index:
				self.__main_index[resource] = VDOM_resource_descriptor.convert(self.__old_index[resource])
				self.__name_index[self.__old_index[resource].name.lower()] = resource
		else:
			self.__main_index = {}
			self.__name_index = {}
			for (owner_id, res_id, name) in managers.storage.list_resource_index():
				self.__main_index[res_id] = VDOM_resource_descriptor(owner_id, res_id) 
				self.__name_index[name.split(".")[0].lower()] = res_id
				
		del self.__old_index
		#TODO: check for not existing or temporary resources
		if not self.__main_index:
			self.remove_resources()
			
	def collect_unused(self):
		"""Removing unused resources with no dependences"""
		pass
		#is_dirty_index = False
		#remove_list = []
		#for id in self.__index:
			#if self.__index[id].use_counting and len(self.__index[id].dependences) == 0:
				#self.__index[id].decrease(None, True)
				#remove_list.append(id)
		#for id in remove_list:
			#self.__index.pop(id)
			#is_dirty_index = True
		#if is_dirty_index and self.save_index: 
			#managers.storage.write_object_async(VDOM_CONFIG["RESOURCE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
			
	def check_resource(self, owner_id, attributes, crc=None):
		if not "id" in attributes:
			return False
		if not attributes["id"] in self.__main_index:
			return False
		resource = self.__main_index[attributes["id"]].load_copy()
		if resource.application_id != owner_id:# and owner_id not in resource.dependences:
			return False
		if not resource.filename:
			return False
		if not managers.file_manager.exists(file_access.resource, owner_id ,None, resource.filename):
			return False
		#if crc != managers.file_manager.compute_crc(file_access.resource,resource.application_id,resource.object_id, resource.filename):
			#return False
		return True
		
	def add_resource(self, owner_id, object_id, attributes, bin_data):
		"new version of Add resource"
		if attributes.get("id") in self.__main_index:
			#We have such resource already
			resource = self.__main_index[attributes.get("id")]
			resource.load_copy()
			if not managers.file_manager.exists(file_access.resource, owner_id ,None, resource.filename):
				managers.file_manager.write(file_access.resource,resource.application_id,object_id, resource.filename, bin_data,None, "save_async" in attributes)
			return attributes.get("id")
		else:
			assert(isinstance(attributes, dict))
			write_async = False
			object_owner = None
			if "label" in attributes and (object_id,attributes["label"]) in self.__label_index:
				return self.__label_index[(object_id,attributes["label"])].id
			res_descriptor = VDOM_resource_descriptor(owner_id,attributes.get("id"))
			
			self.__main_index[res_descriptor.id] = res_descriptor
			if "label" in attributes:
				self.__label_index[(object_id,attributes["label"])] = res_descriptor
				res_descriptor.object_id = object_id
			else:
				res_descriptor = copy.copy(res_descriptor)
			for key in attributes:
				if key == "name":
					setattr(res_descriptor,"name",unicode(attributes["name"]).encode('ascii','ignore'))
					self.__name_index[res_descriptor.name.lower()] = res_descriptor.id
				elif key == "save_async":
					write_async = True
				elif key !="id":
					setattr(res_descriptor,key,attributes[key])
			if "res_type" not in attributes:
				res_descriptor.res_type = "permanent"
			if "res_format" not in attributes:
				res_descriptor.res_format = ""
				
			managers.file_manager.write(file_access.resource,res_descriptor.application_id,object_id, res_descriptor.filename, bin_data,None, write_async)
			if "label" not in attributes:
				res_descriptor.save_record()			
		return res_descriptor.id
	
	def add_resource_old(self, owner_id, object_id, attributes, bin_data):
		"""Adding a new resource"""
		if "id" in attributes and attributes["id"] in self.__index and object_id:
			self.__index[attributes["id"]].increase(object_id)
		else:
			write_async = False
			if "label" in attributes and (object_id,attributes["label"]) in self.__label_index:
				return self.__label_index[(object_id,attributes["label"])].id
			else:
				if "id" not in attributes:
					attributes["id"] = str(utils.uuid.uuid4())
				resource = VDOM_resource_object(owner_id,object_id,attributes["id"])
			try:
				for key in attributes:
					if key == "name":
						setattr(resource,"name",unicode(attributes["name"]).encode('ascii','ignore'))
					elif key == "save_async":
						write_async = True
					elif key != "id":
						setattr(resource,key,attributes[key])
			except:
				pass
			self.__index[resource.id] = resource
			temp_owner = None
			if "label" in attributes:
				self.__label_index[(object_id,attributes["label"])] = resource
				if len(resource.dependences) == 1:
					temp_owner = resource.dependences[resource.dependences.keys()[0]]
			managers.file_manager.write(file_access.resource,resource.application_id,temp_owner, resource.filename, bin_data,None, write_async)
		if self.save_index:
			managers.storage.write_object_async(VDOM_CONFIG["RESOURCE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
		return attributes["id"]

	def get_resource(self, owner_id, res_id):
		"""Getting resource object"""
		res = self.__main_index.get(res_id) or self.__main_index.get(self.__name_index.get(res_id.lower()))
		return res.load_copy() if res else None
	
	def get_resource_old(self, owner_id, res_id):
		"""Getting resource object"""
		return self.__index.get(res_id)

	
	def get_resource_by_label(self, object_id, label):
		"""Getting resource object"""
		return self.__label_index.get((object_id,label))



	def list_resources(self, owner_id):
		"""listing of all resources of application"""
		return [res.id for res in self.__main_index.itervalues() if not owner_id or res.application_id == owner_id]
		#result = {}
		#for key in self.__index:
			#if self.__index[key].application_id == owner_id or owner_id in self.__index[key].dependences:
				#result[key] = self.__index[key].id
		#return result
	
	def update_resource(self, owner_id, resource_id, bin_data):
		"""Adding a new resource"""
		if resource_id in self.__main_index and self.__main_index[resource_id].application_id == owner_id:
			res = self.__main_index[resource_id].load_copy()
			managers.file_manager.write(file_access.resource,owner_id,None, res.filename, bin_data)
		#if resource_id in self.__index:
			#managers.file_manager.write(file_access.resource,owner_id,None, self.__index[resource_id].filename, bin_data)
			#return resource_id
		#else:
			#return None
	
	def delete_resource(self,object_id, res_id, remove = False):
		"""Removing resource object and it's content"""
		#TODO: remove resource from label_index
		if res_id in self.__main_index:
			resource = self.__main_index[res_id]
			resource.decrease(object_id,remove)
			if remove:
				if getattr(resource, "object_id",None):
					self.__label_index.pop((resource.object_id,resource.label),None) #TODO: fix labels resources
				self.__main_index.pop(res_id)
				if resource.name in self.__name_index:
					self.__name_index.pop(resource.name.lower())
			
		#if id in self.__index:
			#resource = self.__index[id]
			#resource.decrease(object_id,remove)
			#if remove:
				#if resource.label:
					#self.__label_index.pop(resource.label)
				#self.__index.pop(id)
			#if self.save_index:
				#managers.storage.write_object_async(VDOM_CONFIG["RESOURCE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
			

	def remove_resources(self):
		"""Clearing resource cache on startup"""
		# from src!.storage import storage
		self.__main_index = {}
		self.__label_index = {}
		managers.file_manager.clear(file_access.resource,None, None)

		managers.storage.clear_resources_index() # ?????
		
		#managers.file_manager.clear(file_access.resource,None, None)
		#self.__index = {}
		#if self.save_index:
			#managers.storage.write_object_async(VDOM_CONFIG["RESOURCE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
		#self.__label_index = {}

	def invalidate_resources(self, object_id):
		"""Invalidate and clear all resources by object_id"""
		for (obj_id, label) in self.__label_index.keys():
			if obj_id == object_id:
				del self.__label_index[(obj_id, label)]
				
		managers.file_manager.clear(file_access.resource, None, object_id)		
		for res_id in self.__main_index.keys():
			if self.__main_index[res_id].application_id == object_id:
				del self.__main_index[res_id]
				
		#for (obj_id, label) in self.__label_index.keys():
			#if obj_id == object_id:
				#id = self.__label_index.pop((obj_id, label)).id
				#self.__index.pop(id, None)
		#i = {}
		#for id in self.__index:
			#if self.__index[id].application_id == object_id:#  or object_id in self.__index[id].dependences:
				#i[id] = None
		#for id in i:
			#del self.__index[id]
##		if self.save_index:
		#managers.file_manager.clear(file_access.resource, None, object_id)

	def save_index_off(self):
		"""Turning flag of index saving OFF"""
		self.save_index = False

	def save_index_on(self, forced_save=False):
		"""Turning flag of index saving ON"""
		self.save_index = True
		#if forced_save:
		#	managers.storage.write_object_async(VDOM_CONFIG["RESOURCE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
