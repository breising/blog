from functions import hash_str, make_secure_val, check_secure_val, make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging

def auth(user_id_cookie_hashed):
	#AUTHENTICATE
	#if user is authenticated then go...
	user_id = check_secure_val(user_id_cookie_hashed)
	if user_id == False:
		return False
	else:
		return user_id

class LandPage(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))

		if user_id:
			self.redirect("/welcome")
		else:
			self.redirect("/login")