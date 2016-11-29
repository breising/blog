from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging


class DeleteComment(BlogHandler):
    '''
    DeleteComment handler: get funx renders the deletecomment.hmtl page if the user is the author of the comment. post funx deletes the comment if user is the author.
    '''

    def get(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))

        commentId = self.request.get("commentId")
        postId = self.request.get("postId")

        try:
            q = BlogEntry.get_by_id(int(postId))
        except:
            pass
        if q:
            title = q.title
            body = q.body
            created = q.created
            last_mod = q.last_mod
            author_id = q.author_id
            k = q.key()

        try:
            u2 = Users.get_by_id(int(author_id))
            c = Comments.get_by_id(int(commentId), parent=k)
            u = Users.get_by_id(int(cauthor_id))
        except:
            pass
        if u2:
            blogAuthor = u2.userName
        if c:
            ccreated = c.created
            cbody = c.comment
            cauthor_id = c.author_id
        if c:
            if u:
                cauthor = u.userName

        if user_id:
            # ONLY AUTHOR CAN delete: check that user_id matches the AUTHOR
            if user_id == cauthor_id:
                self.render("deletecomment.html", title=title, body=body, created=created, last_mod=last_mod, author_id=author_id,
                            ccreated=ccreated, cauthor=cauthor, postId=postId, commentId=commentId, author=blogAuthor, cbody=cbody)
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

        try:
            q = BlogEntry.get_by_id(int(postId))
            k = q.key()
        except:
            pass

        # must be logged in
        if user_id:
            try:
            comEntity = Comments.get_by_id(int(commentId), parent=k)
            except:
                pass
        if comEntity:
            # author must be logged in
            if user_id == comEntity.author_id:
                try:
                    c = Comments.get_by_id(int(commentId), parent=k)
                except:
                    pass
                if c:
                    c.delete()

                error = "Post deleted"
                self.redirect("/welcome?error=%s" % error)
            else:
                error = "Only the author can delete."
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
        else:
            error = "Please signup and login to edit posts."
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))
