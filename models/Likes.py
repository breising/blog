from google.appengine.ext import db

class Likes(db.Model):
	user_key = db.StringProperty(required = True)