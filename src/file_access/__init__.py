
from manager import VDOM_file_manager
from share import VDOM_share
from daemon import VDOM_file_manager_writer

application_xml = 0 # XML
global_type 	= 1 # app/types/                           - XML files of types
cache 		= 2 # app/applications/<id>/cache/         - Swap for source manager
resource        = 3 # app/resources/<owner_id>/            - Application's and type's resources
type_source     = 4 # app/objects/                         - Runtime cache for Engine
database        = 5 # app/databases/<owner_id>/            - Application's databases
storage         = 6 # app/storage/<id>/                    - Application storage with base64'd filenames
certificate     = 7 # app/cert/                            - Server SSL certificates