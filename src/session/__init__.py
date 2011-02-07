from manager import internal_session_manager as session_manager
import src.managers
src.managers.reg_manager("session_manager", session_manager)
