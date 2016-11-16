from google.appengine.ext import db

class Comments(db.Model):
	comment = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	author_id = db.StringProperty(required = True)
	author_name = db.StringProperty(required = True)
