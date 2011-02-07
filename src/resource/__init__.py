from manager import internal_resource_manager as resource_manager
from editor import internal_resource_editor
import src.managers
src.managers.reg_manager("resource_manager", resource_manager)
src.managers.reg_manager("resource_editor", internal_resource_editor)
