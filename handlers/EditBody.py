from functions import hash_str, make_secure_val, check_secure_val, make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging

class EditBody(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))

		title = self.request.get("title")

		if user_id:
			try:
				# query db filtered by title to get body and author
				q = BlogEntry.all().filter('title =', title).get()
				# old is the original text before changes
				old = q.body
				author = q.author

				if user_id:
					if author == user_id:
						
						self.render("edit-body.html", old = old, title = title)
					else:
						error = "You are not the author. Only the author can edit."
						self.redirect("/focus?title=%s&error=%s" % (title,error))
			  	else:
			  		self.redirect("/login")
			except:
			  	error = "Could not access the database."
				self.redirect("/focus?title=%s&error=%s" % (title,error))
		else:
			error = "Please signup and login to edit posts."
			self.redirect("/focus?title=%s&error=%s" % (title,error))

	def post(self):
		try:
			title = self.request.get("title")
		  	body = self.request.get("body")
		  	old = self.request.get("old")

		  	if body == "":
		  		error = "You must enter a new body. Copy the current body if you want no changes."
		  		self.render("edit-body.html", error=error, title=title, old = old)
		 		return
		  	if body:
			  	q = gBlogEntry.all().filter('title =', title).get()
				q.body = body
			 	q.put()

			 	# create delay to allow db to update
			  	def go():
			  		return

				t = Timer(0.2, go)
			  	t.start()

			  	self.redirect("/welcome")
		except:
			error = "Sorry. Could not access the database. Data not saved."
			self.redirect("/focus?title=%s&error=%s" % (title,error))