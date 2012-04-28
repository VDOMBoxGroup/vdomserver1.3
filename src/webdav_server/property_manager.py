from wsgidav.property_manager import PropertyManager
import managers

class VDOM_property_manager(PropertyManager):

	def __init__(self):
		self._app_id = None
		self._obj_id = None
		super(VDOM_property_manager, self).__init__()
		
	def _get_app_id(self):
		return getattr(self, "_app_id")
	
	def _set_app_id(self, value):
		self._app_id = value
		
	def _get_obj_id(self):
		return getattr(self, "_obj_id")
	
	def _set_obj_id(self, value):
		self._obj_id = value

	def _lazyOpen(self):
		self._lock.acquireWrite()
		try:
			# Test again within the critical section
			if self._loaded:
				return True
			# Open with writeback=False, which is faster, but we have to be 
			# careful to re-assign values to _dict after modifying them
			self._dict = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, "getAllProperties", "","")
			self._loaded = True
		finally:
			self._lock.release()
			
	def update(self, normurl):
		self._lock.acquireWrite()
		try:
			if not self._loaded:
				self._lazyOpen()
			self._dict[normurl] = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, "getResourseProperties", "", """{"path": "%s"}""" % normurl)
		finally:
			self._lock.release()
			
	def sync(self):
		self._loaded = False
		
	def getAllProperties(self):
		if not self._loaded:
			self._lazyOpen()
		return self._dict
	
	app_id = property(_get_app_id, _set_app_id)
	obj_id = property(_get_obj_id, _set_obj_id)