from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth

from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging


class EditPost(BlogHandler):
    '''
    EditPost handler: get request renders the edit-post.html page if the user is the author....Post request processes input from the edits and saves new info to the db.
    '''

    def get(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))

        postId = self.request.get("postId")

        if user_id:
            try:
                u = Users.get_by_id(int(user_id))
                q = BlogEntry.get_by_id(int(postId))
            except:
                pass
            if q:
                title = q.title
                body = q.body
                created = q.created
                last_mod = q.last_mod
                author = q.author_id
                k = q.key()
            try:
                comments = Comments.all().ancestor(k)
            except:
                pass
            # if user is the author then ok to edit
            if user_id == author:
                self.render(
                    "edit-post.html", body=body, title=title, postId=postId)
            else:
                error = "You must be author to edit."
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
        else:
            error = "Please signup and login to edit posts."
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))

    def post(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))

        postId = self.request.get("postId")

        if user_id:
            try:
                u = Users.get_by_id(int(user_id))
                q = BlogEntry.get_by_id(int(postId))
            except:
                pass
            if q:
                title = q.title
                body = q.body
                created = q.created
                last_mod = q.last_mod
                author = q.author_id
                k = q.key()

            try:
                comments = Comments.all().ancestor(k)
            except:
                pass
            # check again if user is the author..
            if user_id == author:
                title = self.request.get("title")
                body = self.request.get("body")
                postId = self.request.get("postId")

                # if field is left empty
                if title == "":
                    error = "You must enter a new title."
                    self.redirect(
                        "/editpost?postId=%s&error=%s" % (postId, error))
                if body == "":
                    error = "You must enter new content."
                    self.redirect(
                        "/editpost?postId=%s&error=%s" % (postId, error))
                else:
                    if q:
                        q.title = title
                        q.body = body
                        q.put()

                        error = "Updated post."
                        self.redirect("/focus?postId=%s&error=%s" %
                                  (postId, error))
                    else:
                        error = "error updating post"
                        self.redirect("/focus?postId=%s&error=%s" %
                                  (postId, error))
            else:
                error = "You must be author to edit."
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
        else:
            error = "Please signup and login to edit posts."
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))
