
from names import APPLICATION_SECTION, APPLICATION_ON_START, APPLICATION_ON_FINISH
from manager import internal_xml_manager as xml_manager

import managers


managers.reg_manager("xml_manager", xml_manager)
