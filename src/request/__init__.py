from manager import internal_request_manager as request_manager
import managers
managers.reg_manager("request_manager", request_manager)
