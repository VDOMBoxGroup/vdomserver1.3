
import sys

sys.path.append(VDOM_CONFIG["SOURCE-MODULES-DIRECTORY"])

from swap import internal_swap as swap
from cache import internal_cache as cache
from compiler import internal_compiler as compiler
from dispatcher import internal_dispatcher as dispatcher
import src.managers
src.managers.reg_manager("source_swap", swap)
src.managers.reg_manager("source_cache", cache)
src.managers.reg_manager("compiler", compiler)
src.managers.reg_manager("dispatcher", dispatcher)
