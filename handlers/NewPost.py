from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users


class NewPost(BlogHandler):

    """
    class NewPost is handler for get/post request: renders the new post form and processes submitted data to record a new blog post in the db
    Inherits from Bloghandler
    """
    # make a function that just renders the newpost page so that we can call
    # it from both get and post functions...default values are set to ""

    def render_newpost(self, title="", body="", error=""):
        # with these variables set, the user provided info is preserved when
        # editing
        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        # AUTHENTICATE check for valid cookie
        user_id = None
        user_id = auth(self.request.cookies.get('user_id'))
        if not user_id:
            error = "Please log in."
            self.redirect("/login?error=%s" % error)
        # if the cookie is authentic, then also check username against the db
        else:
            self.render_newpost()

    def post(self):

        # AUTHENTICATE
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))

        title = self.request.get("title")
        body = self.request.get("body")
        like = 0

        if user_id:
            if title and body:
                u = Users.get_by_id(int(user_id))
                b = BlogEntry(title=title, body=body, author_name=u.userName,likes=like, author_id=user_id)
                b.put()

                self.redirect("/welcome")

            else:
                error = "Please provide BOTH a title and body."
                # must include all the parameters below to preserve user
                # entered data
                self.render_newpost(title=title, body=body, error=error)
        else:
            self.redirect("/login")
