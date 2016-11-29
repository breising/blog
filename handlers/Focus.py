from functions import hash_str, make_secure_val, check_secure_val,\
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str,\
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users

class Focus(BlogHandler):
    '''
    Focus handleer, get renders the focus.html page which shows the detail
    of a blog entry along with comments and edit/delete options for the post.
    Post handles the "like" button only.
    '''
    def get(self):
        user_id = None
        # AUTHENTICATE check for valid cookie
        user_id = auth(self.request.cookies.get('user_id'))
        
        if user_id:
            # get the logged in user
            try:
                u2 = Users.get_by_id(int(user_id))
            except:
                pass
            if u2:
                # get the username NOT the id
                user_name = u2.userName
            
            postId = self.request.get("postId")
            error = self.request.get("error")

            q = None
            # querie BlogEntry for the blog entity filtered by title
            try:
                q = BlogEntry.get_by_id(int(postId))
                title = q.title
                body = q.body
                created = q.created
                last_mod = q.last_mod
                author_id = q.author_id
                k = q.key()
            except:
                pass

            if q:
                # get the user who is the author of the blogpost
                try:
                    u = Users.get_by_id(int(author_id))
                except:
                    pass
                if u:
                    # get the authors username NOT id
                    author = u.userName

                comments = None

                # get all comments for this blogpost
                try:
                    comments = Comments.all().ancestor(k)
                except:
                    pass
                # if there are no comments....
                if not comments:
                    commentError = "No comments"
                else:
                    commentError = ""
            else:
                error = "Could not access the blog post."
                self.redirect("/welcome?error=%s" % error)


            # count likes in the database for display, all relevant likes are\
            # ancestors of the blog post with title
            count = 0
            likes = None

            try:
                likes = Likes.all().ancestor(k)
            except:
                pass

            if likes:
                # iterate through all likes for this post to count them
                for like in likes:
                    if like.user_id:
                        count += 1

            self.render("focus.html", postId=postId, title=title,
                        body=body, created=created, last_mod=last_mod,
                        author=author, comments=comments, error=error,
                        count=count, commentError=commentError, user_name=user_name)
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

        # get the logged in user to get username
        

        if user_id:

            try:
            u = Users.get_by_id(int(user_id))
            except:
                pass
            if u:
                user_name = u.userName

            # query for the usual blogPost entity properties
            try:
                q = BlogEntry.get_by_id(int(postId))
                if q:
                    title = q.title
                    body = q.body
                    created = q.created
                    last_mod = q.last_mod
                    author = u.userName
                    author_id = q.author_id
                    # k is the key to the blog post.
                    k = q.key()
            except:
                pass
            try:
                # get all comments for for the blogpost - that means get
                # all comments who are ancestors of K (the blogpost).
                comments = Comments.all().ancestor(k)
            except:
                pass

            # check if user has already liked this post
            # all Likes have a user_id property which corresponds to the
            # User who LIKED the post, so query Likes filtered by user_id
            # to get ALL the likes for this user
            try:
                z = Likes.all().filter("user_id =", user_id)
            except:
                pass
            # then get the ONE (if theres is one) that is an ancestor
            # of the blog post
            if z:
                try:
                    alreadyLiked = z.ancestor(k).get()
                except:
                    pass
            # set flag default = go
            flag = "go"
            # if there are ZERO likes in the db, you'll get an error bc
            # the query gets nothing. To prevent the error, use try/except
            try:
                if alreadyLiked.user_id:
                    flag = "nogo"
            except:
                pass
            
            # initialize the counter
            count = 0
            # If the logged in user is the author then error
            if user_id == author_id:
                # repaint page
                likes = Likes.all().ancestor(k)
                count = 0

                for like in likes:
                    try:
                        if like.user_id:
                            count += 1
                    except:
                        pass

                error = "You can't like your own posts."
                render_focus(title, body, created, last_mod, author,
                             comments, count, error, postId, user_name)
            else:
                # if the logged in user has already liked this post then error
                if flag == "nogo":
                    error = "Stop it....You already liked this post."
                    likes = Likes.all().ancestor(k)
                    count = 0
                    if likes:
                        for like in likes:
                            if like.user_id:
                                count += 1
                    # repaint page
                    render_focus(title, body, created, last_mod, author,
                                 comments, count, error, postId, user_name)
                else:
                    # if tests are passed....record the LIKE;
                    # record the userIDKEY in LIKES as a CHILD of the BLOGPOST
                    # increment the like so it updates the display (not the db)
                    # record like in the db - user_id is the only property and
                    # it's ancestor is the blogpost k.
                    try:
                        l = Likes(parent=k, user_id=user_id)
                    except:
                        pass 
                    
                    if l:
                        l.put()

                    error = "The Like was recorded."
                    # count ALL the existing LIKES to update display \
                    # on VIEW post
                    # filter by ancestor bc ALL likes are recorded as an \
                    # ancestor of ONE blogPost
                    likes = Likes.all().ancestor(k)
                    count = 0

                    if likes:
                        for like in likes:
                            if like.user_id:
                                count += 1

                    # repaint page
                    render_focus(title, body, created, last_mod, author,
                                 comments, count, error, postId, user_name)

        else:
            error = "Please signup and login to like a post."
            # if you are not logged in, you must sign up and login.
            self.redirect("/focus?postId=%s&error=%s" % (postId, error))
