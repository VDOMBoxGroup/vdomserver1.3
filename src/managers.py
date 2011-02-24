
def reg_manager(name, manager):
	globals()[name]=manager_class

def register(name, manager_class):
	globals()[name]=manager_class()
