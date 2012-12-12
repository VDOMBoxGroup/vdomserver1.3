import poplib
import time
from .message import MailAttachment, Message
from utils.exception import VDOM_mailserver_invalid_index
class VDOM_Pop3_client(object):
	def __init__(self, server,port=110, secure=False):
		self.server = server
		self.port = port
		self.secure = secure
		self.message_count=0
		self.read_mails_count = 0
		if self.secure:
			self.connection = poplib.POP3_SSL(self.server, self.port)
		else:
			self.connection = poplib.POP3(self.server, self.port)		
		self.connected = True
		
	def user(self, login, passw):
		self.connection.user(login.encode('utf8'))
		self.connection.pass_(passw.encode('utf8'))	
		try:
			self.message_count = self.connection.stat()[0]
		except:
			self.connected = False
		
	def __len__(self) :
		"Return the number of messages at POP-server"
		try:
			self.message_count = self.connection.stat()[0]
		except:
			self.connected = False
	
	def quit(self):
		self.connection.quit()	
		
	def fetch_message(self,id,delete=False):
		if not self.connected:
			return None
		if id >= self.message_count:
			raise VDOM_mailserver_invalid_index(id)
		email_id = str(self.connection.uidl(id+1).split()[2])
		email_size = str(self.connection.list(id+1).split(" ")[2])
		email_content_decode = ""
		email_content = '\n'.join(self.connection.retr(id+1)[1])
		msg = Message.fromstring(email_content,email_id)
		if delete:
			self.connection.dele(id+1)
		return msg
	
	def fetch_all_messages(self,offset=0,limit=0, delete=False):
		if not self.connected:
			return []
		emails = []
		mail_number = -1
		for i in xrange(offset, min(limit or self.message_count,self.message_count)):
			mail_number = i+1
			emails.append(self.fetch_message(i,delete))
		self.read_mails_count = mail_number
		return emails