from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

class VDOM_webdav_server(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""