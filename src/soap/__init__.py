from server import internal_soap_server as soap_server
import src.managers
src.managers.reg_manager("soap_server", soap_server)
