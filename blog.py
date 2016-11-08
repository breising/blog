import os
import re
from hsec import make_secret
import random
import hmac
from bcrypt import bcrypt
from string import letters
import webapp2
import jinja2
import logging
from threading import Timer

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def hash_str(s):
	return hmac.new(make_secret(),s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))

def check_secure_val(hashPlus):
	if hashPlus:
		val = hashPlus.split('|')[0]
		if hashPlus == make_secure_val(val):
			return val
		else:
			return False

def make_bcrypt_hash(password):
	return bcrypt.hashpw(password, bcrypt.gensalt(2))

def validate_bcrypt(submittedPass, hash):
# get the salt value from the hash (it's the value after the comma)
	hashed2 = bcrypt.hashpw(submittedPass, hash)
	if hashed2 == hash:
		return True
	else:
		return False

def make_cookie_hash(numberV):
	salt = make_salt()
	#make a hash value of the concatenation of name pw and salt
	#sha256 good for cookies but not for passwords: use bcrypt instead
	h = hashlib.sha256(numberV + salt).hexdigest()
	return "%s,%s" %(h,salt)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Likes(db.Model):
	user_key = db.StringProperty(required = True)

class Comments(db.Model):
	comment = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	author = db.StringProperty(required = True)

class BlogEntry(db.Model):
	# required means you must include data in this field or will fail.
	title = db.StringProperty(required = True)
	body = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_mod = db.DateTimeProperty(auto_now = True)
	author = db.StringProperty(required = True)
	# author should be the userID of the logged in user.

class Users(db.Model):
	userName = db.StringProperty(required = True)
	userEmail = db.StringProperty(required = True)
	userPasswordHash = db.StringProperty(required = True)
	userLikes = db.StringProperty()

def auth(user_id_cookie_hashed):
	#AUTHENTICATE
	#if user is authenticated then go...
	user_id = check_secure_val(user_id_cookie_hashed)
	if user_id == False:
		return False
	else:
		return user_id

class Welcome(BlogHandler):
	def get(self):
		try:
			#GET ALL BLOG POSTS TO LIST THEM
			posts = BlogEntry.all().order('-created')

			# # AUTHENTICATE check for valid cookie
			user_id = auth(self.request.cookies.get('user_id'))

			if not user_id:
				error = "Please log in."
				self.redirect("/login?error=%s" % error)
			# if the cookie is authentic, then also check username against the db
			else:
				# TRY bc if there is nothing in the db youll get an error
				try:
					# query db for the userName
					u = Users.all().filter("userName =", user_id).get()
					# if user_id is also in the db, then authenticated
					if u.userName == user_id:
						# show the main page with list of blog posts
						self.render("blogMain.html", user_id = user_id, posts = posts)	
					else:
						# if user is NOT in the db
						error = "Username not in the database."
						self.redirect("/login?error=%s" % error)
				# if user is NOT authenticated via a cookie
				except:
					error = "Error accessing database."
					self.redirect("/login?error=%s" % error)
		except:
			error = "Error accessing database."
			self.redirect("/login?error=%s" % error)

class EditTitle(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))
		
		title = self.request.get("title")

		if user_id:
			try:
				q = BlogEntry.all().filter('title =', title).get()
				body = q.body
				created = q.created
				last_mod = q.last_mod
				author = q.author

				k = q.key()
				comments = Comments.all().ancestor(k)

				if author == user_id:
					old = title
					self.render("edit-title.html", old=old, title=title)
				else:
					error = "You must be author to edit."
					self.redirect("/focus?title=%s&error=%s" % (title,error))
			except:
				error = "Could not access the database."
				self.redirect("/focus?title=%s&error=%s" % (title,error))
		else:
			error = "Please signup and login to edit posts."
			self.redirect("/focus?title=%s&error=%s" % (title,error))
		

	def post(self):
		try:
			new = self.request.get("new")
		  	old = self.request.get("old")

		  	# if field is left empty
		  	if new == "":
		  		error = "You must enter a new title."
		  		self.render("edit-title.html", error=error, old=old)
		  		return
		  	if new:
			  	q = BlogEntry.all().filter('title =', old).get()
				q.title = new
			 	q.put()

			 	# create a delay to give db chance to update
			  	def go():
			  		return

				t = Timer(0.2, go)
			  	t.start()

			  	self.redirect("/welcome")
		except:
			error = "Could not access the database."
			self.redirect("/focus?title=%s&error=%s" % (title,error))
		  
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

class DeletePost(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))
		
		title = self.request.get("title")

		if user_id:
			q = BlogEntry.all().filter('title =', title).get()

			body = q.body
			created = q.created
			last_mod = q.last_mod
			author = q.author

			# ONLY AUTHOR CAN EDIT: check that user_id matches the AUTHOR
			if user_id:
				if author == user_id:
					self.render("delete.html", title=title, body=body, created = created, last_mod = last_mod, author = author)
				else:
					error = "You are not the author of this post. Only the author can delete."
					self.redirect("/focus?title=%s&error=%s" % (title,error))
		  	else:
		  		self.redirect("/login")
		else:
			error = "Please signup and login to edit posts."
			self.redirect("/focus?title=%s&error=%s" %(title,error))


	def post(self):
		try:
			title = self.request.get("title")

			q = BlogEntry.all().filter('title =', title).get()
			q.delete()

			# create delay for db to update
			def go():
		  		#self.redirect("/welcome")
		  		return

			t = Timer(1, go)
		  	t.start()
			self.redirect("/welcome")
		except:
			error = "Error accessing the database. Post may not be deleted."
			self.redirect("/focus?title=%s&error=%s" %(title,error))

class Focus(BlogHandler):
	def get(self):
		title = self.request.get("title")
		error = self.request.get("error")

		#querie BlogEntry for the blog entity filtered by title
		q = BlogEntry.all().filter("title =", title).get()

		body = q.body
		created = q.created
		last_mod = q.last_mod
		author = q.author

		k = q.key()
		comments = Comments.all().ancestor(k)

		#count likes in the database for display, all relevant likes are ancestors of the blog post with title
		likes = Likes.all().ancestor(k)
		count = 0
		for like in likes:
			count += 1

		# self.redirect("/edit/title")
		self.render("focus.html", title=title, body=body, created = created, last_mod = last_mod, author = author, comments = comments, error=error,count=count)

	def post(self):
		def render_focus(title, body, created, last_mod, author, comments, count, error):
			self.render("focus.html", title=title, body=body, created = created, last_mod = last_mod, author = author, comments = comments, count = count, error=error)

		title = self.request.get("title")
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))

		if user_id:
			# has the user already liked this post ?
			# first, query Users filtered by user_id 
			u = Users.all().filter("userName =", user_id).get()

			# then get the key().id() and coerce a string
			user_key = u.key().id()
			user_key = str(user_key)

			# query for the usual blogPost entity properties
			q = BlogEntry.all().filter('title =', title).get()
			body = q.body
			created = q.created
			last_mod = q.last_mod
			author = q.author

			# k is the key to the blog post.
			k = q.key()

			# count ALL the existing LIKES for display on VIEW post
			# filter by ancestor bc ALL likes are recorded as an ancestor of ONE blogPost
			count = 0
			likes = Likes.all().ancestor(k)
			for like in likes:
				count += 1
			
			# check if user has already liked this post
			# all Likes have a user_key property which corresponds to the User who LIKED the post, so query Likes filtered by user_key
			z = Likes.all().filter("user_key =", user_key)
			# if you get a result it means User already liked this post
			alreadyLiked = z.ancestor(k).get()
			# set flag default 
			flag = "go"
			# if there are ZERO likes in the db, you'll get an error bc the query gets nothing. To prevent the error, use try/except
			try:
				if alreadyLiked.user_key == user_key:
					flag = "nogo"
			except:
				pass

			# get all comments for for the blogpost - that means get all comments who are ancestors of K (the blogpost).
			comments = Comments.all().ancestor(k)

			# If the logged in user is the author then...
			if user_id == q.author:
				#repaint page
				error = "You are the author. You can't like your own posts."
				render_focus(title, body, created, last_mod, author, comments, count, error)
			else:
				# if the logged in user has already liked this post then...
				if flag == "nogo":
					error = "You already liked this post."
					#repaint page
					render_focus(title, body, created, last_mod, author, comments, count, error)
				else:
					# if tests are passed....record the LIKE; 
					# record the userIDKEY in LIKES as a CHILD of the BLOGPOST
					#increment the like so it updates the display (not the db)
					count = count + 1
					# record like in the db - user_key is the only property and it's ancestor is the blogpost k.
					l = Likes(parent = k, user_key = user_key)
					l.put()
					error = "The Like was recorded."
					#repaint page
					render_focus(title, body, created, last_mod, author, comments, count, error)
		else:
			error = "Please signup and login to like a post."
			# if you are not logged in, you must sign up and login.
			self.redirect("/focus?title=%s&error=%s" % (title,error))


class Login(BlogHandler):
	def get(self):
		#GET ALL BLOG POSTS TO LIST THEM
		posts = BlogEntry.all().order('-created')

		# get any error messages from get request
		error = self.request.get("error")

		self.render("login.html",error=error,posts=posts)

	def post(self):
		try:
			# get name and password from the get request
			name = self.request.get("username")
			submittedPassword = self.request.get("password")
			
			# query the Users db by the userName
			u = Users.all().filter('userName =', name).get()
			# u = the entity object

			if u:
				# get the hashed password from the u object
				dbHashedPassword = u.userPasswordHash
				if dbHashedPassword:
					# authenticate the hash password
					if validate_bcrypt(submittedPassword, dbHashedPassword):
						# make a new username hash to create a login cookie for this user for the next time they return
						userNameHash_cookie_val = str(make_secure_val(u.userName))
						# set the cookie
						self.response.headers.add_header('Set-Cookie', 'user_id=%s' % userNameHash_cookie_val)
						# with the new cookie set, /welcome will do the auto login

						def go():
			  				return

						t = Timer(1, go)
			  			t.start()
			  			self.redirect("/welcome")
						
					else:
						error = "Login failed. Password is incorrect."
						self.render("login.html", error=error)
			else:
				error = "Login failed. Username is incorrect."
				self.render("login.html", error=error)
		except:
			error = "Sorry. Could not access the database."
			self.render("login.html", error=error)

class Signup(BlogHandler):
	def get(self):
		self.render("sign-up.html")
	def post(self):
		try:
			# get the data from the post request
			userName = self.request.get("userName")
			password = self.request.get("password")
			passwordV = self.request.get("passwordV")
			userEmail = self.request.get("userEmail")

			# if all the fields are completed
			if userName and password and passwordV and userEmail:
				# if passwords do NOT match
				if password == passwordV:
					

					q = Users.all().filter("userName =", userName).get()
					# if not q means the userName IS allowed
					if not q:
						# look up the user name to verify it's not already in the db first.
						# make the password hash with bcrypt
						userPasswordHash = make_bcrypt_hash(password)

						# record username and password hashes in the db
						s = Users(userName=userName,userPasswordHash=userPasswordHash,userEmail=userEmail)
						s.put()
						
						self.redirect("/welcome")
					# if q yes, means that userName is NOT unique so,
					else:
						error = "Please choose a different username."
						self.render("sign-up.html", error=error)
				# passwords DO NOT match
				else:
					error2="Passwords must match."
					self.render("sign-up.html", error=error)
					
			# if any field is not completed
			else:
				error = "Please complete all the fields"
				self.render("sign-up.html", error=error)
		except:
			error = "Error could not sign in. Could not access the database."
			self.render("sign-up.html", error=error)

class NewPost(BlogHandler):
	#make a function that just renders the newpost page so that we can call it from both get and post functions...default values are set to ""
	def render_newpost(self, title="", body="", error=""):
		#with these variables set, the user provided info is preserved when editing
		self.render("newpost.html",title = title, body = body, error = error)

	def get(self):
		self.render_newpost()

	def post(self):
		try:
			title = self.request.get("title")
			body = self.request.get("body")
			like = 0

			#AUTHENTICATE
			user_id = None
			# AUTHENTICATE check for valid cookie
			user_id = auth(self.request.cookies.get('user_id'))
				
			if user_id:
				if title and body:
					u = Users.all().filter("userName =", user_id).get()

					user_key = u.key().id()
					user_keyid = str(user_key)

					b = BlogEntry(title=title,body=body,author=user_id,likes=like)
					b.put()

					logging.warning(user_key)

					l = Likes(parent = b, user_key = user_keyid)
					l.put()

					def delay():
			  			#self.redirect("/welcome")
			  			return
			  		
					t = Timer(1, delay)
			  		t.start()

					self.redirect("/welcome")
					
				else:
					error="Please provide BOTH a title and body."
					# must include all the parameters below to preserve user entered data
					self.render_newpost(title=title,body=body,error=error)
		  	else:
		  		self.redirect("/login")
		except:
		  	error = "Could not access database. Post not saved."
		  	self.render_newpost(title=title,body=body,error=error)

class Comment(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))

		title = self.request.get("title")

		if user_id:
			try:
				title = self.request.get("title")
				q = BlogEntry.all().filter('title =', title).get()

				body = q.body

				self.render("comment.html", title = title, body = body)
			except:
				error = "Could not access database."
				self.render("comment.html", title = title, body = body)
		else:
			error = "Please signup and login to edit comments."
			# if you are not logged in, you must sign up and login.
			self.redirect("/focus?title=%s&error=%s" % (title,error))

	def post(self):
		try:
			comment = None
			title = self.request.get("title")
			comment = self.request.get("comment")
			
			q = BlogEntry.all().filter('title =', title).get()

			#AUTHENTICATE
			user_id = None
			# AUTHENTICATE check for valid cookie
			user_id = auth(self.request.cookies.get('user_id'))

			if user_id:
				if comment:
					c = Comments(parent = q, comment=comment, author=user_id)
					c.put()
					self.redirect("/focus?title=%s" % title)
				else:
					error = "Please add a comment."
					# must include all the parameters below to preserve user entered data
					self.render("comment.html", title=title, body=body, error=error)
		  	else:
		  		error = "Please signup and login to edit comments"
		  		self.redirect("/focus?title=%s" % (title,error))
		except:
			error = "Could not access the database."
			self.render("comment.html", title=title, body=body, error=error)
class EditComment(BlogHandler):
	def get(self):
		commentId = None
		commentId = self.request.get("commentId")
		title = self.request.get("title")

		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))
		
		if user_id:
			c = Comments.get(commentId)
			author = c.author
			
			if user_id == author:

			  		c = Comments.get(commentId)
					author = c.author
					comment = c.comment
					created = c.created

			  		self.render("edit-comment.html", author=author, comment=comment, created=created, commentId=commentId, title=title)
			else:
				error = "You must be the author to edit the comment."
			  	self.redirect("/focus?title=%s&error=%s" % (title, error))
		else:
				error = "You must be loggen in to edit the comment."
			  	self.redirect("/focus?title=%s&error=%s" % (title, error))

	def post(self):
		comment = self.request.get("comment")
		title = self.request.get("title")
		commentId = self.request.get("commentId")

		q = Comments.get(commentId)

		q.comment = comment
		q.put()

		error = ""
		self.redirect("/focus?title=%s&error=%s" % (title, error))

class Logout(BlogHandler):
	def post(self):
		self.response.headers.add_header("Set-Cookie", "user_id=deleted; Expires=Thu, 01-Jan-1970 00:00:00 GMT")
		error = "You are now logged out."
		self.redirect("/welcome")
		
class LandPage(BlogHandler):
	def get(self):
		user_id = None
		# AUTHENTICATE check for valid cookie
		user_id = auth(self.request.cookies.get('user_id'))

		if user_id:
			self.redirect("/welcome")
		else:
			self.redirect("/login")

app = webapp2.WSGIApplication([('/', LandPage),
								('/welcome', Welcome),
								('/comment', Comment),
								('/delete', DeletePost),
								('/focus', Focus),
								('/login', Login),
								('/signup', Signup),
								('/newpost', NewPost),
								('/edit/title', EditTitle),
								('/edit/body', EditBody),
								('/logout', Logout),
								('/edit/comment', EditComment)
                               ],
                              debug=True)