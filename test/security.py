import unittest, sys

import src.security
from src.security.protected_object import VDOM_protected_object
import src.security.access as access


class TEST(unittest.TestCase):
	"""Xml manager module test class"""

	def test1(self):
		"""user basic opperations"""
		um = src.security.user_manager
		user = um.create_user("User1", "123123")
		um.match_user("User1", "324234")
		um.match_user("User123", "123123")
		um.match_user("User1", "123123")
		um.remove_user(user)
		um.match_user("User1", "123123")
		return True

	def test2(self):
		"""acl storage test"""
		um = src.security.user_manager

		user = um.match_user("User", "123123")
		if( user == None ):
			sys.stderr.write( "creating user" )
			user = um.create_user("User", "123123")

		p = VDOM_protected_object()
		p.id = "OBJECT_ID"
		sys.stderr.write( str(p.have_access(user, access.read)) )

	def test3(self):
		"""basic acl operations"""
		um = src.security.user_manager
		user = um.match_user("User", "123123")
		p = VDOM_protected_object()
		p.id = "OBJECT_ID"
		p.add_access_rule(user, access.read, True)

		sys.stderr.write( str(p.have_access(user, access.read)) )
		sys.stderr.write( str(p.have_access(user, access.write)) )
 		#p.remove_access_rule(user, access.read)
		#print p.have_access(user, access.read)

	def test4(self):
		"""wait for async write"""
		import time
		time.sleep(0.1)

	def test5(self):
		"""root and guest users"""
		um = src.security.user_manager
		sys.stderr.write( um.get_root_user().id + " ")
		sys.stderr.write( um.get_guest_user().id )
	def test6(self):
		"""root access"""
		um = src.security.user_manager
		p = VDOM_protected_object()
		p.id = "OBJECT_ID"
 		sys.stderr.write( str(p.have_access(um.get_root_user(), access.read)) + " " )
 		sys.stderr.write( str(p.have_access(um.get_root_user(), access.write)) + " " )
