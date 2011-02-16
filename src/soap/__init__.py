from server import internal_soap_server as soap_server
import managers
managers.reg_manager("soap_server", soap_server)
