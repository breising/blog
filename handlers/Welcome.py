
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
from functions import hash_str, make_secure_val, check_secure_val, make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, set_secure_cookie, login, auth
import logging

class Welcome(BlogHandler):
	def get(self):
			#GET ALL BLOG POSTS TO LIST THEM
			posts = BlogEntry.all().order('-created')

			# # AUTHENTICATE check for valid cookie
			user_id = auth(self.request.cookies.get('user_id'))

			if not user_id:
				error = "Please log in."
				self.redirect("/login?error=%s" % error)
			# if the cookie is authentic, then also check username against the db
			else:
				# query db for the userName to check whether user has been manually removed from db.
				u = Users.get_by_id(int(user_id))
				logging.warning(u)

				# if user_id is also in the db, then authenticated
				if u:
					userName = u.userName
					# show the main page with list of blog posts
					self.render("blogMain.html", user_id = userName, posts = posts)	
				else:
					# if user is NOT in the db
					error = "Username not in the database."
					self.redirect("/login?error=%s" % error)
			
