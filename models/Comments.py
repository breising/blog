from google.appengine.ext import db

class Comments(db.Model):
	comment = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	author = db.StringProperty(required = True)