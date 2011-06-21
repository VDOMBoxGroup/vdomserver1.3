
import managers, version, utils


class VDOM_server(object):

	def _get_version(self):
		return version.VDOM_server_version
	
	def _get_guid(self):
		return utils.uuid.uuid4()
	
	version=property(_get_version)
	mailer=property(lambda self: managers.email_manager)
	guid=property(_get_guid)
