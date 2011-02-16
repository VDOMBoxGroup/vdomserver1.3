from manager import internal_session_manager as session_manager
import managers
managers.reg_manager("session_manager", session_manager)
