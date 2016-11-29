from functions import hash_str, make_secure_val, check_secure_val, \
	make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth

from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users

class Logout(BlogHandler):
	'''
	Logout handles post request from main/welcome page...
	Deletes the users cookie to log them out.
	'''
    def post(self):
        self.response.headers.add_header(
            "Set-Cookie", "user_id=deleted; Expires=Thu, 01-Jan-1970 00:00:00 GMT")
        error = "You are now logged out."
        self.redirect("/welcome")
