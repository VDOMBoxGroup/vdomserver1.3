import thread, time, email, email.generator, copy
from smtplib import SMTP,SMTP_SSL,SMTPConnectError,SMTPHeloError,SMTPAuthenticationError,SMTPException,SMTPRecipientsRefused,SMTPSenderRefused,SMTPDataError,SSLFakeFile
from socket import create_connection, error as socket_error
from ssl import PROTOCOL_SSLv23, PROTOCOL_SSLv3, PROTOCOL_TLSv1, wrap_socket
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.mime.multipart  import MIMEMultipart
from collections import namedtuple
from utils.semaphore import VDOM_semaphore
from storage.storage import VDOM_config
import managers
from daemon import VDOM_mailer

MailAttachment = namedtuple("MailAttachment","data, filename, content_type, content_subtype")

class VDOM_SMTP(SMTP):
	
	def __init__(self, host = '', port = 0, local_hostname = None):
		cf = VDOM_config()
		self.tout = cf.get_opt("SMTP-SENDMAIL-TIMEOUT")
		if None == self.tout: self.tout = 30.0
		self.tout = float(self.tout)
		self.use_ssl = cf.get_opt("SMTP-OVER-SSL")
		if None == self.use_ssl: self.use_ssl = 0
		SMTP.__init__(self, host = '', port = 0, local_hostname = None)

	def getreply(self):
		self.sock.settimeout(self.tout)
		return SMTP.getreply(self)
	
	def _get_socket(self, host, port, timeout):
		new_socket = create_connection((host, port), timeout)
		if self.use_ssl != 0:
			ssl_version = PROTOCOL_SSLv23 if self.use_ssl == 1 else PROTOCOL_TLSv1
			new_socket = wrap_socket(new_socket, ssl_version=ssl_version)
			self.file = SSLFakeFile(new_socket)
		return new_socket



class MIME_VDOM(MIMENonMultipart):

	def __init__(self, _data, _type, _subtype, _encoder=encoders.encode_base64, **_params):
		MIMENonMultipart.__init__(self, _type, _subtype, **_params)
		self.set_payload(_data)
		_encoder(self)


class VDOM_email_manager(object):

	def __init__(self):
		self.__sem = VDOM_semaphore()
		self.__queue = []
		self.__errors = {}
		self.__error = ""
		self.__id = 0
		self.__load_config()
		self.__daemon=VDOM_mailer(self)
		self.__daemon.start()

	def __load_config(self):
		cf = VDOM_config()
		self.smtp_server = cf.get_opt("SMTP-SERVER-ADDRESS")
		if not self.smtp_server: self.smtp_server = "smtp.gmail.com"
		self.smtp_port = cf.get_opt("SMTP-SERVER-PORT")
		if not self.smtp_port: self.smtp_port = 465
		self.smtp_user = cf.get_opt("SMTP-SERVER-USER")
		if not self.smtp_user: self.smtp_user = "Vdom.Server@gmail.com"
		self.smtp_pass = cf.get_opt("SMTP-SERVER-PASSWORD")
		if not self.smtp_pass: self.smtp_pass = "VDMNK22YK"
		self.use_ssl = cf.get_opt("SMTP-OVER-SSL")
		if not self.use_ssl: self.use_ssl = 1
		self.smtp_sender = cf.get_opt("SMTP-SERVER-SENDER")
		if not self.smtp_sender: self.smtp_sender = ""
		try:
			self.smtp_port = int(self.smtp_port)
		except:
			self.smtp_port = 25

	def send(self, fr, to, subj, msg, attach = [],ttl=50,reply=""):	# attach item must be a tuple (data, filename, content_type, content_subtype)
		self.__load_config()		
		if not self.smtp_server:
			return None
		self.__sem.lock()
		try:
			x = self.__id
			
			if self.smtp_sender and self.smtp_sender.find("@")!=-1:
				sender = self.smtp_sender
			else:
				sender = self.smtp_user
			if fr:
				sender = "%s <%s>"%(fr,sender)

			m = {"from": sender, "to": to, "subj": subj, "msg" : msg, "id": x, "attach": attach,"ttl":ttl}
			if reply:
				m['reply-to'] = reply
			self.__queue.append(m)
			self.__id += 1
			return x
		finally:
			self.__sem.unlock()

	def check(self, _id):	# check if there was error when sending message, pass here the value returned by .send
		"""return string if there was error, return None if no error"""
		self.__sem.lock()
		x = None
		if _id in self.__errors:
			x = self.__errors[_id]
		self.__sem.unlock()
		return x

	def check_connection(self):
		self.__sem.lock()
		try:		
			self.__load_config()
			s = VDOM_SMTP()
			#connecting
			s.connect(self.smtp_server, self.smtp_port)
			self.__error = ""
			#authentification
			if "" != self.smtp_user:
				s.login(self.smtp_user, self.smtp_pass)
				self.__error = ""
			s.quit()
			del s		
		except (SMTPConnectError,SMTPHeloError,socket_error) as e: #Connect error
			debug("SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port))
			self.__error = "SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port)
			managers.log_manager.error_server("SMTP connect error: %s on %s:%d" % (str(e),self.smtp_server, self.smtp_port), "email")
		except SMTPAuthenticationError as e:
			#debug("Authentication error: %s" % str(e))
			self.__error = "SMTP Authentication error: %s" % str(e)
			managers.log_manager.error_server("SMTP authentication error: %s" % str(e), "email")		
		except SMTPException, e:
			self.__error = "General SMTP error: %s" % str(e)
		except Exception, e:
			self.__error = "Unknown error: %s" % str(e)
		finally:
			self.__sem.unlock()
		return self.status()
			
	def cancel(self, _id):
		"""cancel email if it has not been sent, return True if email has been successfully cancelled"""
		x = False
		self.__sem.lock()
		i = -1
		for q in self.__queue:
			if _id == q["id"]:
				i = self.__queue.index(q)
				break
		if i >= 0:
			self.__queue.pop(i)
			self.__errors.pop(_id, 0)
			x = True
		self.__sem.unlock()
		return x

	def status(self):
		"""check is there was smtp connect or authentication error"""
		self.__sem.lock()
		x = copy.deepcopy(self.__error)
		self.__sem.unlock()
		return x
	
	def clear_queue(self):
		self.__sem.lock()
		self.__queue = []
		self.__errors = []
		self.__error = ""
		self.__id = 0
		self.__sem.unlock()
		
	def get_queue(self):
		self.__sem.lock()
		x = copy.deepcopy(self.__queue)
		self.__sem.unlock()
		return x
	
	def work(self):
			ts=0.1
			if len(self.__queue) > 0:
				self.__sem.lock()
				try:
					self.__load_config()
					if not self.smtp_server:
						raise SMTPConnectError(0,"No server adress in config")
					s = VDOM_SMTP()
					#connecting
					s.connect(self.smtp_server, self.smtp_port)
					self.__error = ""
					#authentification
					if "" != self.smtp_user:
						s.login(self.smtp_user, self.smtp_pass)
						self.__error = ""

					self.__queue_tmp = []
					ts = 0.1
					while len(self.__queue) > 0:
						item = self.__queue.pop(0)
						item["ttl"]-=1
						msg = MIMEMultipart()
						subject = item["subj"]
						if isinstance(subject, unicode):
							subject = subject.encode("utf-8")
						msg['Subject'] = subject
						msg['From'] = item["from"]# +" <vdom.server@gmail.com>" if self.smtp_user.lower() == "vdom.server@gmail.com" and item["from"].lower().find("vdom.server@gmail.com")==-1 else item["from"]
						msg['To'] = item["to"]
						if 'reply-to' in item:
							msg['Reply-to'] = item['reply-to']
						msgbody = item.get("msg")
						if  msgbody:
							if isinstance(msgbody, unicode):
								msgbody = msgbody.encode("utf-8")
							text2 = MIMEText(msgbody)
							text2.set_type("text/html")
							text2.set_charset("utf-8")
							msg.attach(text2)
						attach = item.get("attach",[])
						for a in attach:
							a1 = MIME_VDOM(a[0], *a[2:])
							if a[1]:
								a1.add_header('content-disposition', 'attachment', filename=a[1])
								a1.add_header('content-location', a[1])
							msg.attach(a1)
						try:
							s.sendmail(item["from"], item["to"].split(","), msg.as_string())
							self.__errors.pop(item["id"], 0)
						except (SMTPRecipientsRefused,SMTPSenderRefused,SMTPDataError) as e:
							debug("SMTP send to %s error: %s" % (item["to"], str(e)))
							managers.log_manager.error_server("SMTP send to %s error: %s" % (item["to"], str(e)), "email")
							self.__errors[item["id"]] = str(e)
							# move this mail to the temp queue
							if item["ttl"] >0:
								self.__queue_tmp.append(item)
						except Exception as e:
							self.__errors[item["id"]] = str(e)
							# move this mail to the temp queue
							if item["ttl"] >0:
								self.__queue_tmp.append(item)
							self.__queue_tmp.append(item)
							raise
					if len(self.__queue_tmp) > 0:
						self.__queue = self.__queue_tmp #[item for item in self.__queue_tmp if item["attempt"]<50]
						del self.__queue_tmp
						ts = 30
					s.quit()
					del s

					
				except (SMTPConnectError,SMTPHeloError,socket_error) as e: #Connect error
					debug("SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port))
					self.__error = "SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port)
					managers.log_manager.error_server("SMTP connect error: %s on %s:%d" % (str(e),self.smtp_server, self.smtp_port), "email")
					#del s
					ts = 360
				except SMTPAuthenticationError as e:
					#debug("Authentication error: %s" % str(e))
					self.__error = "SMTP Authentication error: %s" % str(e)
					managers.log_manager.error_server("SMTP authentication error: %s" % str(e), "email")
					#del s
					
					ts = 360
				
				except SMTPException, e:
					self.__error = "General SMTP error: %s" % str(e)
					ts = 30
				except Exception, e:
					self.__error = "Unknown error: %s" % str(e)
					ts = 5
				finally:
					self.__sem.unlock()
			else:
				ts = 10
			#time.sleep(ts)
			return ts
