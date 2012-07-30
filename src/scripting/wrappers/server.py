
import managers, version, utils
from vscript.engine import vcompile, vexecute


class VDOM_vscript(object):

	def execute(self, source, use=None, **keywords):
		environment={"v_%s"%name: value for name, value in keywords.iteritems()}
		code, vsource=vcompile(source, environment=environment, use=use)
		vexecute(code, vsource, environment=environment, use=use)

class VDOM_server(object):

	def __init__(self):
		self._vscript=VDOM_vscript()

	def _get_version(self):
		return version.VDOM_server_version
	
	def _get_guid(self):
		return utils.uuid.uuid4()
	
	version=property(_get_version)
	mailer=property(lambda self: managers.email_manager)
	guid=property(_get_guid)
	vscript=property(lambda self: self._vscript)
