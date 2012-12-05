from collections import namedtuple
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.mime.multipart  import MIMEMultipart
MailAttachment = namedtuple("MailAttachment","data, filename, content_type, content_subtype")
MailContentType = namedtuple("MailContentType","type, charset, params")

class MIME_VDOM(MIMENonMultipart):

	def __init__(self, _data, _type, _subtype, _encoder=encoders.encode_base64, **_params):
		MIMENonMultipart.__init__(self, _type, _subtype, **_params)
		self.set_payload(_data)
		_encoder(self)
		
class Message():
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
		self.content_type = []
		self.ttl = 50
		convertmap = {"id":"id","sender":"sender","from":"from_email", "to":"to_email", "subj":"subject", "msg":"body", "attach": "attach","ttl":"ttl","reply":"reply_to", "headers":"headers", "no_multipart": "nomultipart", "content_type":"content_type"}
		for key,value in kw.iteritems():
			if key in convertmap:
				setattr(self,convertmap[key],value)
		if isinstance(self.to_email, list) and len(self.to_email)>0:
			self.to_email = ", ".join(self.to_email)
				
	def append(self, attachment):
		if isinstance(attachment,MailAttachment):
			self.attach.append(attachment)
		else:
			pass#add processing tuple
			self.attach.append(attachment)

	
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
				a1 = MIME_VDOM(a[0], *a[2:])
				if a[1]:
					a1.add_header('content-disposition', 'attachment', filename=a[1])
					a1.add_header('content-location', a[1])
				msg.attach(a1)
		
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