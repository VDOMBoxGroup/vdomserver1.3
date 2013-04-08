import managers
from utils.semaphore import VDOM_semaphore
from utils.uuid import uuid4
from utils.file_argument import File_argument, Attachment
import time
def run(request):
	sess = request.session()
	for uploaded_file in request.files.itervalues():
		fileid = str(uuid4())
		uploaded_file.autoremove = False
		#managers.file_manager.file_upload[fileid] = attach
		sess.files[fileid] = uploaded_file
		request.write(str(fileid)+'\n')