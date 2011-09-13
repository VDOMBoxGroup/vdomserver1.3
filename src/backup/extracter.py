import managers, tempfile, os
from utils.app_management import import_application

class VDOM_extracter(object):
    def __init__(self, app_id):
        self.app_id = app_id
        self.e_map = {"application": VDOM_app_extracter}
        
    def get_extracters(self, app_id):
        return dict([(key, value(app_id)) for key, value in self.e_map.items()])
    
    def extract(self):
        pass
    def restore(self, path):
        pass
    
class VDOM_app_extracter(VDOM_extracter):
    
    def extract(self):
        path = tempfile.mkdtemp("", "", os.path.join(VDOM_CONFIG["TEMP-DIRECTORY"], self.app_id))
        
        try:
            managers.xml_manager.export_application(self.app_id, "xml", path)
            return path
        except:
            return None
    
    def restore(self, path):
        """import app_xml"""
        if os.path.exists(path):
            import_application(path)
        else:
            pass
    