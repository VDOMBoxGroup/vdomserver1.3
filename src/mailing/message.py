from collections import namedtuple
import time
import email
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.mime.multipart  import MIMEMultipart
from utils.uuid import uuid4
#MailAttachment = namedtuple("MailAttachment","data, filename, content_type, content_subtype")
MailContentType = namedtuple("MailContentType","type, charset, params")

class MIME_VDOM(MIMENonMultipart):

	def __init__(self, _data, _type, _subtype, _encoder=encoders.encode_base64, **_params):
		MIMENonMultipart.__init__(self, _type, _subtype, **_params)
		self.set_payload(_data)
		_encoder(self)
		
class MailAttachment(object):
	def __init__(self, data=None, filename="", content_type="application", content_subtype="octet-stream"):
		self.data = None
		self.filename = ""
		self.content_type = None
		self.content_subtype = None
		
	@classmethod
	def fromtuple(self, t):
		attach = self()
		if len(t)==4:
			attach.data, attach.filename, attach.content_type, attach.content_subtype = t		
		return attach
	
	def as_mime(self):
		attach = MIME_VDOM(self.data, self.content_type,self.content_subtype)
		if self.filename:
			attach.add_header('content-disposition', 'attachment', filename=self.filename)
			attach.add_header('content-location', self.filename)
		return attach
	
	
class Message(object):
	def __init__(self,**kw):
		self.id = 0
		self.subject 	= None
		self.sender = None
		self.from_email = None
		self.reply_to = None
		self.to_email 	= ""
		self.attach	= []
		self.body	= None
		self.date 	= None
		self.nomultipart = False
		self.headers = {}
		self.content_type = tuple()
		self.ttl = 50
		self.priority = "normal"
		convertmap = {"id":"id","sender":"sender","from":"from_email", "to":"to_email", "subj":"subject", "msg":"body", "attach": "attach","ttl":"ttl","reply":"reply_to", "headers":"headers", "no_multipart": "nomultipart", "content_type":"content_type"}
		for key,value in kw.iteritems():
			if key in convertmap:
				if key=="attach":
					value = [msg if isinstance(msg,MailAttachment) else MailAttachment.fromtuple(msg) for msg in value]
				setattr(self,convertmap[key],value)
		if isinstance(self.to_email, list) and len(self.to_email)>0:
			self.to_email = ", ".join(self.to_email)
				
	def append(self, attachment):
		if self.nomultipart:
			raise Exception("Non Multipart message cannot have attachment")
		if isinstance(attachment,MailAttachment):
			self.attach.append(attachment)
		elif isinstance(attachment, tuple):
			self.attach.append(MailAttachment.fromtuple(attachment))

	
	def as_mime(self):
		#rewrite this code to return MIME object
		
		if self.nomultipart:
			msgbody = self.body
			if isinstance(msgbody, unicode):
				msgbody = msgbody.encode("utf-8")
			msg = MIMEText(msgbody)
			if len(self.content_type)>1: #item["content_type"] == (type, charset, params={})
				msg.set_type(self.content_type[0])
				msg.set_charset(self.content_type[1])								
				if len(self.content_type)>2 and self.content_type[2]:
					for key,value in self.content_type[2].iteritems():
						msg.set_param(key,value)
			else:
				msg.set_type("text/html")
				msg.set_charset("utf-8")
		else:
			msg = MIMEMultipart()
			msgbody = self.body
			if  msgbody:
				if isinstance(msgbody, unicode):
					msgbody = msgbody.encode("utf-8")
				text2 = MIMEText(msgbody)
				text2.set_type("text/html")
				text2.set_charset("utf-8")
				msg.attach(text2)
			attach = self.attach
			for a in attach:
				msg.attach(a.as_mime())
		
		subject = self.subject
		if isinstance(subject, unicode):
			subject = subject.encode("utf-8")
		msg['Subject'] = subject
		msg['From'] = self.from_email
		msg['To'] = self.to_email
		if self.reply_to:
			msg['Reply-to'] = self.reply_to
		if self.headers:
			for key,value in item["headers"].iteritems():
				msg[key] = value
		
		return msg.as_string()
	@classmethod
	def fromstring(self, mimestring, email_id):
		msg = Message()
		msg.id = email_id
		mail = email.message_from_string(mimestring)
		msg.parse_body(mail)
		codecs = [msg.content_type[1], 'utf8', 'cp1252', 'latin1' ]
		
		try:
			subject = email.Header.decode_header(mail.get('Subject'))
			msg.subject		= subject[0][0].decode(subject[0][1]) if subject[0][1] else decode_strings(subject[0][0], codecs)
		except Exception, ex:
			msg.subject = ""
			
	
		try:
			from_email = email.Header.decode_header(mail.get('From'))
			msg.from_email	= from_email[0][0].decode(from_email[0][1]) if from_email[0][1] else decode_strings(from_email[0][0], codecs)
		except Exception, ex:
			msg.from_email = ""
			
	
		try:
			to_email = email.Header.decode_header(mail.get('To'))
			msg.to_email	= to_email[0][0].decode(to_email[0][1]) if to_email[0][1] else decode_strings(to_email[0][0], codecs)
		except Exception, ex:
			msg.to_email = ""
			
		if mail.get('Date'):
			date = mail.get('Date')
			msg.date = time.strftime("%d %b %Y",email.utils.parsedate(date))
			msg.date_in_sec	= str(time.mktime(email.utils.parsedate(date)))
		else:
			msg.date = time.strftime("%d %b %Y")
			msg.date_in_sec	= str(time.mktime(time.localtime()))
			
		try:
			mail_type = email.Header.decode_header(mail.get('Content-Type'))
			if mail_type and "plain" in mail_type[0][0]:
				msg.mail_type = "plain"
			else:
				msg.mail_type = "html"
		except Exception, ex:		
			msg.mail_type = "html"
			
		if "X-Priority" in mail:
			priority = re.search('\d', mail["X-Priority"])
			if priority:
				msg.priority = "high" if priority.group(0) == "1" else "normal"		
			
		return msg
	
	def parse_body(self,mail):
		body = ""
		self.content_type = MailContentType("text/html","utf8",{})
		body_charset = "utf8"
		#TODO: check this code for multipart messages with different attachments
		if mail.is_multipart():
			for part in mail.walk():
				if part.get_content_maintype() == "multipart":
					boundary = ""
					double_data = "False"
		
					for p in range(len(part.get_payload())):
						if part.get_boundary() and boundary == part.get_boundary():
							double_data = "True"
						else:
							double_data = "False"
						boundary = part.get_boundary()
						for subpart in part.get_payload(p).walk():
							if ("content-disposition" in subpart and "attachment" in subpart["content-disposition"]):
								oAttach = subpart.get_payload()
								guid = str(uuid4())
		
								#application.storage.write(guid, base64.b64decode(oAttach))
		
								attachment_object = MailAttachment()
								attachment_object.guid = guid
								attachment_object.data = base64.b64decode(oAttach)
		
								try:
									filename = email.Header.decode_header(subpart.get_filename())
									attachment_object.filename = filename[0][0].decode(filename[0][1]) if filename[0][1] else filename[0][0]
								except:
									attachment_object.filename = subpart.get_filename()
		
								attachment_object.mail_id = ""
								attachment_object.location = "inbox"
								
								self.attach.append(attachment_object)
							else:
								if double_data == "True":
									body = ""
								if "Content-Type" in subpart and "charset" in subpart["Content-Type"]:
									body_charset = subpart["Content-Type"].split('=')[1]
								if "Content-Transfer-Encoding" in subpart and subpart["Content-Transfer-Encoding"].lower() == "base64":
									try:
										body += base64.b64decode(subpart.get_payload())
									except Exception, ex:
										pass
								elif "Content-Transfer-Encoding" in subpart and subpart["Content-Transfer-Encoding"].lower() == "quoted-printable":
									import quopri
									try:
										body += quopri.decodestring(subpart.get_payload())
									except Exception, ex:
										pass
								else:
									if not isinstance(subpart.get_payload(), list):
										body += subpart.get_payload()
		
		else:
			if "Content-Type" in mail and "charset" in mail["Content-Type"]:
				body_charset = mail["Content-Type"].split('=')[1]
			if "Content-Transfer-Encoding" in mail and mail["Content-Transfer-Encoding"].lower() == "base64":
				try:
					body += base64.b64decode(mail.get_payload())
				except Exception, ex:
					pass
			elif "Content-Transfer-Encoding" in mail and mail["Content-Transfer-Encoding"].lower() == "quoted-printable":
				import quopri
				try:
					body += quopri.decodestring(mail.get_payload())
				except Exception, ex:
					pass
			else:
				if not isinstance(mail.get_payload(), list):
					body += mail.get_payload()
		self.body = decode_strings(body,[body_charset, 'utf8', 'cp1252'])

def decode_strings(text, codecs_list):
	if type( text ) == unicode:
		return text

	# if unknown encoding, try decode with latin1
	codecs = codecs_list + [ 'latin1' ]

	result = ''
	for codec in codecs:
		try:
			result = text.decode(codec, 'ignore')
			return result
		except:
			continue

	return result