from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging


class DeleteComment(BlogHandler):

    def get(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))

        commentId = self.request.get("commentId")
        postId = self.request.get("postId")

        q = BlogEntry.get_by_id(int(postId))
        title = q.title
        body = q.body
        created = q.created
        last_mod = q.last_mod
        author_id = q.author_id
        k = q.key()

        c = Comments.get_by_id(int(commentId), parent=k)
        ccreated = c.created
        cauthor_name = c.author_name
        cbody = c.comment
        cauthor_id = c.author_id

        if user_id:
            # ONLY AUTHOR CAN delete: check that user_id matches the AUTHOR
            if user_id == cauthor_id:
                self.render("deletecomment.html", title=title, body=body, created=created, last_mod=last_mod, author_id=author_id,
                            ccreated=ccreated, cauthor_name=cauthor_name, cbody=cbody, postId=postId, commentId=commentId)
            else:
                error = "Only the author can delete."
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
        else:
            error = "Please signup and login to delete comments."
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))

    def post(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        commentId = self.request.get("commentId")
        postId = self.request.get("postId")

        q = BlogEntry.get_by_id(int(postId))
        k = q.key()

        # must be logged in
        if user_id:
            comEntity = Comments.get_by_id(int(commentId), parent=k)
            # author must be logged in
            if user_id == comEntity.author_id:

                c = Comments.get_by_id(int(commentId), parent=k)
                c.delete()

                error = "Post deleted"
                self.redirect("/welcome?error=%s" % error)
            else:
                error = "Only the author can delete."
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
        else:
            error = "Please signup and login to edit posts."
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))
