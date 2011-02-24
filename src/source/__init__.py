
import sys
sys.path.append(VDOM_CONFIG["SOURCE-MODULES-DIRECTORY"])

#from swap import internal_swap as swap
#from cache import internal_cache as cache
#from compiler import internal_compiler as compiler
#from dispatcher import internal_dispatcher as dispatcher

#import managers
#managers.reg_manager("source_swap", swap)
#managers.reg_manager("source_cache", cache)
#managers.reg_manager("compiler", compiler)
#managers.reg_manager("dispatcher", dispatcher)

from swap import VDOM_source_swap
from cache import VDOM_source_cache
from compiler import VDOM_compiler
from dispatcher import VDOM_dispatcher
