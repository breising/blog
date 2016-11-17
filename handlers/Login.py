
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
from functions import hash_str, make_secure_val, check_secure_val,\
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
import functions
from threading import Timer
import logging


class Login(BlogHandler):

    def get(self):
        # GET ALL BLOG POSTS TO LIST THEM
        posts = BlogEntry.all().order('-created')

        # get any error messages from get request
        error = self.request.get("error")

        self.render("login.html", error=error, posts=posts)

    def post(self):
        user_id = None
        # get name and password from the request
        name = self.request.get("username")
        submittedPassword = self.request.get("password")
        # query the Users db by the userName, if not there, throw error
        u = Users.all().filter('userName =', name).get()
        # u = the entity object
        if u:
            user_id = u.key().id()
            # get the hashed password from the u object
            dbHashedPassword = u.userPasswordHash
            if dbHashedPassword:
                # authenticate the hash password
                if validate_bcrypt(submittedPassword, dbHashedPassword):
                    # make a new user-key hash to create a login cookie for
                    # this user for the next time they return
                    str_user_id = str(user_id)
                    userKeyHash_cookie_val = str(make_secure_val(str_user_id))
                    # set the cookie
                    self.response.headers.add_header(
                        'Set-Cookie', 'user_id=%s' % userKeyHash_cookie_val)
                    # with the new cookie set, /welcome will do the auto login
                    self.redirect("/welcome")
                else:
                    error = "Login failed. Password is incorrect."
                    self.render("login.html", error=error)
        else:
            error = "Login failed. Username is incorrect."
            self.render("login.html", error=error)
