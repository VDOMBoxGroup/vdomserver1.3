from manager import internal_file_manager as file_manager
from share import internal_share as share
import managers
managers.reg_manager("file_manager", file_manager)
managers.reg_manager("file_share", share)

application_xml = 0 # XML
global_type 	= 1 # app/types/                           - XML files of types
cache 		= 2 # app/applications/<id>/cache/         - Swap for source manager
resource        = 3 # XML
type_source     = 4 # app/objects/                         - Runtime cache for Engine
database        = 5 # XML
