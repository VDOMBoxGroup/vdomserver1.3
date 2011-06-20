
import managers, version


class VDOM_server(object):

	def _get_version(self):
		return version.VDOM_server_version
	
	version=property(_get_version)
	mailer=property(lambda self: managers.email_manager)
