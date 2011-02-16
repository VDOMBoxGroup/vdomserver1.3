
import managers

from compiler import compile_declarations_n_libraries, compile_registations


attribute_name="e2vdom_script"



def process(container, parent):
	request=managers.request_manager.get_request()
	registrations=compile_registations(container, parent)
	if hasattr(request, attribute_name): getattr(request, attribute_name).append(registrations)
	else: setattr(request, attribute_name, [registrations])

def generate(container):
	request=managers.request_manager.get_request()
	declarations, libraries=compile_declarations_n_libraries(container)
	registrations=getattr(request, attribute_name)
	return libraries, declarations, "\n".join(registrations)
