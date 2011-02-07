
import src.managers
from src.xml import APPLICATION_SECTION, APPLICATION_ON_FINISH

def actions_on_shutdown():
	for id in src.managers.xml_manager.get_applications():
		application=src.managers.xml_manager.get_application(id)
		application_actions=application.global_actions[APPLICATION_SECTION]
		action=application_actions[APPLICATION_ON_FINISH]
		if action.code:
			src.engine.engine.special(application, action, namespace={})
