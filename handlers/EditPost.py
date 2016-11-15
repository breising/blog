from functions import hash_str, make_secure_val, check_secure_val, make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, set_secure_cookie, login, auth

from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging

class EditPost(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))
		
		postId = self.request.get("postId")

		if user_id:
			u = Users.get_by_id(int(user_id))

			q = BlogEntry.get_by_id(int(postId))

			title = q.title
			body = q.body
			created = q.created
			last_mod = q.last_mod
			author = q.author

			k = q.key()
			comments = Comments.all().ancestor(k)

			if author == u.userName:
				self.render("edit-post.html", body=body, title=title, postId = postId)
			else:
				error = "You must be author to edit."
				self.redirect("/focus?postId=%s&error=%s" % (postId,error))
		else:
			error = "Please signup and login to edit posts."
			self.redirect("/focus?postId=%s&error=%s" % (postId,error))

	def post(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))
		
		postId = self.request.get("postId")

		if user_id:
			title = self.request.get("title")
		  	body = self.request.get("body")
		  	postId = self.request.get("postId")

		  	# if field is left empty
		  	if title == "":
		  		error = "You must enter a new title."
		  		self.redirect("/editpost?postId=%s&error=%s" % (postId,error))
		  	if body == "":
		  		error = "You must enter new content."
		  		self.redirect("/editpost?postId=%s&error=%s" % (postId,error))
		  	else:
			  	q = BlogEntry.get_by_id(int(postId))

				q.title = title
				q.body = body

			 	q.put()

			  	error = "Updated post."
				self.redirect("/focus?postId=%s&error=%s" % (postId,error))
