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
from models import BlogEntry, Comments, Likes, Users

def hash_str(s):
    '''
    takes a string and makes a hash
    '''
    return hmac.new(make_secret(), s).hexdigest()

def make_secure_val(s):
    '''
    takes a string and a hash and combines them to make a cookie string
    '''
    return "%s|%s" % (s, hash_str(s))

def render_str(self, template, **params):
    return render_str(template, **params)
    
def check_secure_val(hashPlus):
    '''
    takes a cookies string, splits on the pipe, checks authenticity of the
    hash, return password value or false
    '''
    if hashPlus:
        val = hashPlus.split('|')[0]
        if hashPlus == make_secure_val(val):
            return val
        else:
            return False

def make_bcrypt_hash(password):
    '''
    checks the authenticity of the submitted password against a hash
    '''
    return bcrypt.hashpw(password, bcrypt.gensalt(2))


def validate_bcrypt(submittedPass, hash):
    '''
     get the salt value from the hash (it's the value after the comma)
    '''
    hashed2 = bcrypt.hashpw(submittedPass, hash)
    if hashed2 == hash:
        return True
    else:
        return False


def make_cookie_hash(numberV):
    salt = make_salt()
    # make a hash value of the concatenation of name pw and salt
    # sha256 good for cookies but not for passwords: use bcrypt instead
    h = hashlib.sha256(numberV + salt).hexdigest()
    return "%s,%s" % (h, salt)


def set_secure_cookie(self, name, val):
    cookie_val = make_secure_val(val)
    self.response.headers.add_header(
        'Set-Cookie',
        '%s=%s; Path=/' % (name, cookie_val))


def login(self, user):
    self.set_secure_cookie('user_id', str(user.key().id()))


def auth(user_id_cookie_hashed):
    '''
    AUTHENTICATE
    if user is authenticated then go...
    '''
    user_id = check_secure_val(user_id_cookie_hashed)

    return None if not user_id else user_id
