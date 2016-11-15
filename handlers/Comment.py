from functions import hash_str, make_secure_val, check_secure_val, make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging

class Comment(BlogHandler):
	def get(self):
		user_key = None
		# AUTHENTICATE check for valid cookie
		user_key = auth(self.request.cookies.get('user_key'))

		postId = self.request.get("postId")

		if user_key:

			q = BlogEntry.get_by_id(int(postId))
			title = q.title
			body = q.body

			self.render("comment.html", title = title, body = body, postId = postId)
		else:
			error = "Please signup and login to edit comments."
			# if you are not logged in, you must sign up and login.
			self.redirect("/focus?postId=%s&error=%s" % (postId,error))

	def post(self):
		#AUTHENTICATE
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))

		if user_id:
			comment = None
			comment = self.request.get("comment")
			postId= self.request.get("postId")
			
			q = BlogEntry.get_by_id(int(postId))
			u = Users.get_by_id(int(user_id))

			if comment:
				if comment != "":
					c = Comments(parent = q, comment=comment,\
						author = user_id)
					c.put()

					error = "Comment saved."
					self.redirect("/focus?postId=%s&error=%s" % (postId,error))
				else:
					error = "Please add content for the comment or cancel."
					self.redirect("/comment?postId=%s&error=%s" % (postId,error))
			else:
				error = "Please add a comment."
				# must include all the parameters below to preserve user entered data
				self.redirect("/comment?postId=%s&error=%s" % (postId,error))
	  	else:
	  		error = "Please signup and login to add a comment."
	  		self.redirect("/focus?postId=%s&error=%s" % (postId,error))
		