from extracter import VDOM_extracter

class VDOM_backup(object):
    

    def backup(self, app_id, path, meta_info, server_version, vhost="default"):
        
        el = VDOM_extracter.get_extracters(app_id)
        all_path = {key: value.extract() for key, value in el.items()}
        src_path = {key: value for key, value in all_path.items() if value}
        self.__do_backup(app_id, path, src_path, meta_info, server_version, vhost)
        
    def __do_backup(self, app_id, path, src_path, meta_info, server_version, vhost="default"):
        pass
    