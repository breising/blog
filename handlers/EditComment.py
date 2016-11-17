from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users


class EditComment(BlogHandler):

    def get(self):
        commentId = None
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        commentId = self.request.get("commentId")
        postId = self.request.get("postId")

        q = BlogEntry.get_by_id(int(postId))
        k = q.key()
        # must be logged in
        if user_id:
            commentId = int(commentId)
            comment = Comments.get_by_id(commentId, parent=k)

            # must be the author to edit the comment
            if user_id == comment.author_id:

                c = Comments.get_by_id(commentId, parent=k)
                comment = c.comment
                created = c.created
                author_id = c.author_id

                u = Users.get_by_id(int(author_id))
                user_name = u.userName

                self.render("edit-comment.html", author=user_name, comment=comment,
                            created=created, commentId=commentId, postId=postId)
            else:
                error = "You must be the author to edit the comment."
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
        else:
            error = "You must be loggen in to edit the comment."
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))

    def post(self):
        user_id = None
        commentId = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        commentId = self.request.get("commentId")
        comment = self.request.get("comment")
        postId = self.request.get("postId")

        q = BlogEntry.get_by_id(int(postId))
        k = q.key()

        if user_id:
            commentId = int(commentId)
            comEntity = Comments.get_by_id(commentId, parent=k)

            if user_id == comEntity.author_id:
                q = BlogEntry.get_by_id(int(postId))
                k = q.key()

                c = Comments.get_by_id(int(commentId), parent=k)

                c.comment = comment
                c.put()

                error = ""
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
            else:
                error = "You must be the author to edit the comment."
                self.redirect("/focus?postId=%s&error=%s" % (postId, error))
        else:
            error = "You must be loggen in to edit the comment."
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))
