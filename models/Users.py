from google.appengine.ext import db


class Users(db.Model):
    userName = db.StringProperty(required=True)
    userEmail = db.StringProperty(required=True)
    userPasswordHash = db.StringProperty(required=True)
    userLikes = db.StringProperty()
