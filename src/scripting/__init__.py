
from server import VDOM_server
from application import VDOM_application
from session import VDOM_session
from request import VDOM_request
from response import VDOM_response

from obsolete import VDOM_request as VDOM_obsolete


server=VDOM_server()
application=VDOM_application()
session=VDOM_session()
request=VDOM_request()
response=VDOM_response()

obsolete=VDOM_obsolete()
