from manager import internal_database_manager as database_manager
import src.managers
src.managers.reg_manager("database_manager", database_manager)

from dbobject import VDOM_sql_query
from dbobject import VDOM_database_table
