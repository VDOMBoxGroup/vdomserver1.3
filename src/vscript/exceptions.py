
import utils.exception
from . import errors
from .subtypes.error import error


__all__=["v_genericerror", "v_servererror", "v_scripterror",
	"v_subscriptoutofrange", "v_divisionbyzero", "v_overflow"]


v_genericerror=error(errors.python)
v_servererror=error(utils.exception.VDOM_exception)
v_scripterror=error(errors.generic)
v_subscriptoutofrange=error(errors.subscript_out_of_range)
v_divisionbyzero=error(errors.division_by_zero)
v_overflow=error(errors.overflow)
