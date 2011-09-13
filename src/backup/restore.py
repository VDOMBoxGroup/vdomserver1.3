import managers
from extracter import VDOM_extracter

class VDOM_restore(object):
    
    def restore(self, driver_path, app_id, revision_number, dirs=None):
        if not dirs:
            return None
        """
          Here should be instructions, that excec bash scripts to restore. For example:
          ---------------------------------------------------------------
             Popen(command, driver_path, app_id, revision_number, dirs)
          ---------------------------------------------------------------
        """
        el = VDOM_extracter.get_extracters(app_id)
        for key in dirs:
            if key in el:
                el[key].restore(dirs[key])
            
    def list_apps(self, driver_path):
        """
          Here should be instructions, that excec bash scripts, that
          return list of applications, which locate in driver_path
        """
        pass
    
    def revisions(self, driver_path, app_id):
        """
          Here should be instructions, that excec bash scripts, that
          return list of application revisions, which locate in driver_path
        """
        pass
    
    def info(self, driver_path, app_id, revision_number):
        """
          Here should be instructions, that excec bash scripts, that
          return information about revision
        """
        pass
    