from functions import hash_str, make_secure_val, check_secure_val,\
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str,\
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging


class Focus(BlogHandler):

    def get(self):
        # # AUTHENTICATE check for valid cookie
        user_id = None
        user_id = auth(self.request.cookies.get('user_id'))
        u = Users.get_by_id(int(user_id))
        user_name = u.userName

        if user_id:

            postId = self.request.get("postId")
            error = self.request.get("error")

            # querie BlogEntry for the blog entity filtered by title
            q = BlogEntry.get_by_id(int(postId))

            title = q.title
            body = q.body
            created = q.created
            last_mod = q.last_mod
            author_id = q.author_id
            auth

            k = q.key()
            comments = Comments.all().ancestor(k)

            # count likes in the database for display, all relevant likes are\
            # ancestors of the blog post with title
            likes = Likes.all().ancestor(k)
            count = 0

            for like in likes:
                try:
                    if like.user_id:
                        count += 1
                except:
                    pass

            # self.redirect("/edit/title")
            self.render("focus.html", postId=postId, title=title,
                        body=body, created=created, last_mod=last_mod,
                        author=user_name, comments=comments, error=error,
                        count=count, user_name=user_name)
        else:
            self.redirct("/login")

    def post(self):
        def render_focus(title, body, created, last_mod, author, comments,
                         count, error, postId, user_name):

            self.render("focus.html", title=title, body=body,
                        created=created, last_mod=last_mod, author=author,
                        comments=comments, count=count, error=error,
                        postId=postId, user_name=user_name)

        postId = self.request.get("postId")
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        u = Users.get_by_id(int(user_id))
        user_name = u.userName

        if user_id:
            # query for the usual blogPost entity properties
            q = BlogEntry.get_by_id(int(postId))
            title = q.title
            body = q.body
            created = q.created
            last_mod = q.last_mod
            author = q.author
            author_id = q.author_id

            # k is the key to the blog post.
            k = q.key()

            # check if user has already liked this post
            # all Likes have a user_id property which corresponds to the
            # User who LIKED the post, so query Likes filtered by user_id
            # to get ALL the likes for this user
            z = Likes.all().filter("user_id =", user_id)

            # then get the ONE (if theres is one) that is an ancestor
            # of the blog post
            alreadyLiked = z.ancestor(k).get()

            # set flag default
            flag = "go"
            # if there are ZERO likes in the db, you'll get an error bc
            # the query gets nothing. To prevent the error, use try/except
            try:
                if alreadyLiked.user_id:
                    flag = "nogo"
            except:
                pass

            # get all comments for for the blogpost - that means get
            # all comments who are ancestors of K (the blogpost).
            comments = Comments.all().ancestor(k)

            count = 0
            # If the logged in user is the author then...
            logging.warning(author_id + " = " + user_id)

            if user_id == author_id:
                # repaint page
                likes = Likes.all().ancestor(k)
                count = 0

                for like in likes:
                    try:
                        if like.user_id:
                            count += 1
                            pass
                    except:
                        pass

                error = "You can't like your own posts."
                render_focus(title, body, created, last_mod, author,
                             comments, count, error, postId, user_name)
            else:
                # if the logged in user has already liked this post then...
                if flag == "nogo":
                    error = "Stop it....You already liked this post."
                    likes = Likes.all().ancestor(k)
                    count = 0

                    for like in likes:
                        try:
                            if like.user_id:
                                count += 1
                                pass
                        except:
                            pass
                    # repaint page
                    render_focus(title, body, created, last_mod, author,
                                 comments, count, error, postId, user_name)
                else:
                    # if tests are passed....record the LIKE;
                    # record the userIDKEY in LIKES as a CHILD of the BLOGPOST
                    # increment the like so it updates the display (not the db)
                    # record like in the db - user_id is the only property and
                    # it's ancestor is the blogpost k.
                    l = Likes(parent=k, user_id=user_id)
                    l.put()
                    error = "The Like was recorded."
                    # count ALL the existing LIKES to update display \
                    # on VIEW post
                    # filter by ancestor bc ALL likes are recorded as an \
                    # ancestor of ONE blogPost
                    likes = Likes.all().ancestor(k)
                    count = 0

                    for like in likes:
                        try:
                            if like.user_id:
                                count += 1
                                pass
                        except:
                            pass

                    # repaint page
                    render_focus(title, body, created, last_mod, author,
                                 comments, count, error, postId, user_name)

        else:
            error = "Please signup and login to like a post."
            # if you are not logged in, you must sign up and login.
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))
