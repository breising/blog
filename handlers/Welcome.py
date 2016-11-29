from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
import logging

class Welcome(BlogHandler):
    '''
    Welcome handler renders the main page of the blog site after a user is\
    authenticated.
    '''

    def get(self):
        user_id = None
        u = None
        error = ""
        post = ""
        # GET ALL BLOG POSTS TO LIST THEM
        try:
            posts = BlogEntry.all().order('-created')
        except:
            pass

        # AUTHENTICATE: check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))

        if user_id:
            try:
                # check db to verify that the username exists even though \
                # browser has a cookie. Maybe this user was deleted from the\
                # db by the admin.
                u = Users.get_by_id(int(user_id))
            except:
                pass
            if u:
                user_name = u.userName

                try:
                    error = self.request.get("error")
                except:
                    pass
                self.render("blogMain.html", user_name=user_name, posts=posts, error=error)
            else:
                # if user is NOT in the db
                error = "Could not verify username."
                self.redirect("/login?error=%s" % error)
        else:
            error = "Please log in."
            self.redirect("/login?error=%s" % error)

            
