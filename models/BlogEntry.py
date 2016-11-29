from google.appengine.ext import db


class BlogEntry(db.Model):
    # required means you must include data in this field or will fail.
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_mod = db.DateTimeProperty(auto_now=True)
    author_name = db.StringProperty(required=True)
    likes = db.IntegerProperty(required=True)
    author_id = db.StringProperty(required=True)
 
