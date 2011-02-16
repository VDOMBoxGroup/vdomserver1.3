
import util.exception

import errors



__all__=["v_genericerror",
	"v_servererror", "v_scripterror",
	"v_subscriptoutofrange",
	"v_divizionbyzero", "v_overflow"]



v_genericerror=errors.python
v_servererror=util.exception.VDOM_exception
v_scripterror=errors.generic
v_subscriptoutofrange=errors.subscript_out_of_range
v_divizionbyzero=errors.division_by_zero
v_overflow=errors.overflow
