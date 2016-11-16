from functions import hash_str, make_secure_val, check_secure_val, make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging

class DeletePost(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))
		
		postId = self.request.get("postId")

		if user_id:
			q = BlogEntry.get_by_id(int(postId))
			title = q.title
			body = q.body
			created = q.created
			last_mod = q.last_mod
			author = q.author_id

			logging.warning(author + " = " + user_id)

			# ONLY AUTHOR CAN EDIT: check that user_id matches the AUTHOR
			if author == user_id:
				self.render("delete.html", title=title, body=body, created = created, last_mod = last_mod, author = author, postId = postId)
			else:
				error = "Only the author can delete."
				self.redirect("/focus?postId=%s&error=%s" % (postId,error))

		else:
			error = "Please signup and login to edit posts."
			self.redirect("/focus?postId=%s&error=%s" % (postId,error))

	def post(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))

		postId = self.request.get("postId")
		# must be logged in
		if user_id:
			q = BlogEntry.get_by_id(int(postId))
			title = q.title
			body = q.body
			created = q.created
			last_mod = q.last_mod
			author = q.author_id

		# ONLY AUTHOR CAN EDIT: check that user_id matches the AUTHOR
			if author == user_id:
				q = BlogEntry.get_by_id(int(postId))
				q.delete()

				error = "Post deleted"
				self.redirect("/welcome?error=%s" % error)
			else:
				error = "Only the author can delete."
				self.redirect("/focus?postId=%s&error=%s" % (postId,error))

		else:
			error = "Please signup and login to edit posts."
			self.redirect("/focus?postId=%s&error=%s" % (postId,error))


			
		