
import webapp2

from models import BlogEntry, Comments, Likes, Users
from handlers import Welcome, DeletePost, Focus, Login, Logout, Comment, LandPage, NewPost, Signup, EditComment, EditPost

app = webapp2.WSGIApplication([('/', LandPage),
								('/welcome', Welcome),
								('/comment', Comment),
								('/delete', DeletePost),
								('/focus', Focus),
								('/login', Login),
								('/signup', Signup),
								('/newpost', NewPost),
								('/editpost', EditPost),
								('/logout', Logout),
								('/editcomment', EditComment)
                               ],
                              debug=True)

							