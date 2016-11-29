from functions import hash_str, make_secure_val, check_secure_val,\
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth

from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users

class LandPage(BlogHandler):

    def get(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        # above checks for the cookie, if there is not cookie then redirect to the login page else auto-login and show welcome
        if user_id:
            self.redirect("/welcome")
        else:
            self.redirect("/login")
