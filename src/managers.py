
def reg_manager(name, obj):
	globals()[name] = obj

def register_manager(name, manager):
	globals()[name]=manager

def search_manager(name):
	return globals()[name]
