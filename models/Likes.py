from google.appengine.ext import db


class Likes(db.Model):
    user_id = db.StringProperty(required=True)
