from manager import internal_request_manager as request_manager
import src.managers
src.managers.reg_manager("request_manager", request_manager)
