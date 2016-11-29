from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging


class Comment(BlogHandler):
    '''
    Comment handler: get funx renders the comment.html page if the user is auth and the post funx saves the input field data to the db is user is auth.
    '''

    def get(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        # get the blog post id from the get request
        postId = self.request.get("postId")

        if user_id:

            q = BlogEntry.get_by_id(int(postId))
            title = q.title
            body = q.body

            self.render("comment.html", title=title, body=body, postId=postId)
        else:
            error = "Please signup and login to edit comments."
            # if you are not logged in, you must sign up and login.
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))

    def post(self):
        # AUTHENTICATE
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        u = Users.get_by_id(int(user_id))
        user_name = u.userName

        if user_id:
            comment = None
            comment = self.request.get("comment")
            postId = self.request.get("postId")

            q = BlogEntry.get_by_id(int(postId))

            if comment:
                if comment != "":
                    c = Comments(parent=q, comment=comment,
                                 author_id=user_id, author_name=user_name)
                    c.put()

                    error = "Comment saved."
                    self.redirect(
                        "/focus?postId=%s&error=%s&user_name=%s" % (postId, error, user_name))
                else:
                    error = "Please add content for the comment or cancel."
                    self.redirect(
                        "/comment?postId=%s&error=%s&user_name=%s" % (postId, error, user_name))
            else:
                error = "Please add a comment."
                # must include all the parameters below to preserve user
                # entered data
                self.redirect(
                    "/comment?postId=%s&error=%s&user_name=%s" % (postId, error, user_name))
        else:
            error = "Please signup and login to add a comment."
            self.redirect("/focus?postId=%s&error=%s&user_name=%s" %
                          (postId, error, user_name))
