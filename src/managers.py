
def register(name, manager_class):
	globals()[name]=manager_class()

if False: #WING IDE helpers
	from log import VDOM_log_manager
	from storage import VDOM_storage
	from file_access import VDOM_file_manager, VDOM_share
	from resource import VDOM_resource_manager, VDOM_resource_editor
	from database import VDOM_database_manager
	from source import VDOM_source_swap, VDOM_source_cache, VDOM_compiler, VDOM_dispatcher
	from security import VDOM_acl_manager, VDOM_user_manager
	from web import VDOM_vhosting
	from request import VDOM_request_manager
	from engine import VDOM_engine
	from module import VDOM_module_manager
	from session import VDOM_session_manager
	from memory import VDOM_xml_manager
	from mailing import VDOM_email_manager
	from soap import VDOM_soap_server
	from managment import VDOM_server_manager
	from scheduler import VDOM_scheduler_manager
	from backup import VDOM_backup_manager
	from webdav_server import VDOM_webdav_manager
	
	server = VDOM_server()
	log_manager = VDOM_log_manager()
	storage = VDOM_storage()
	file_manager = VDOM_file_manager()
	file_share = VDOM_share()
	resource_manager = VDOM_resource_manager()
	resource_editor = VDOM_resource_editor()
	database_manager = VDOM_database_manager()
	source_swap = VDOM_source_swap()
	source_cache = VDOM_source_cache()
	compiler = VDOM_compiler()
	dispatcher = VDOM_dispatcher()
	acl_manager = VDOM_acl_manager()
	user_manager = VDOM_user_manager()
	virtual_hosts = VDOM_vhosting()
	request_manager = VDOM_request_manager()
	engine = VDOM_engine()
	module_manager = VDOM_module_manager()
	session_manager = VDOM_session_manager()
	scheduler_manager = VDOM_scheduler_manager()
	xml_manager = VDOM_xml_manager()
	email_manager = VDOM_email_manager()
	soap_server = VDOM_soap_server()
	server_manager = VDOM_server_manager()
	backup_manager = VDOM_backup_manager()
	webdav = VDOM_webdav_manager()
	
	from request.request import VDOM_request
	managers.request_manager.current = VDOM_request()
	assert(isinstance(managers.request_manager.current, VDOM_request))
	#from file_access.manager import VDOM_file_manager
	#file_manager = VDOM_file_manager()
	#assert isinstance(globals()[""], )