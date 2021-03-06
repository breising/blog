from functions import hash_str, make_secure_val, check_secure_val, \
    make_bcrypt_hash, validate_bcrypt, make_cookie_hash, render_str, \
    set_secure_cookie, login, auth
from handlers import BlogHandler
from models import BlogEntry, Comments, Likes, Users
import logging


class Signup(BlogHandler):
    '''
    Handler for the signup.html page get and post requests. Post takes the\
    signup data, verifies it, then saves the user info.
    '''

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
                        # make the password hash with bcrypt
                        userPasswordHash = make_bcrypt_hash(password)

                        # record username and password hashes in the db
                        s = Users(
                            userName=userName,
                            userPasswordHash=userPasswordHash,
                            userEmail=userEmail)
                        if s:
                            user_key = s.put()
                        # get the entity from the key
                        user_id = user_key.id()
                        # make a new user-key hash to create a login cookie for
                        # this user for the next time they return
                        str_user_id = str(user_id)
                        userKeyHash_cookie_val = str(make_secure_val(str_user_id))
                        # set the cookie
                        self.response.headers.add_header(
                            'Set-Cookie', 'user_id=%s' 
                            % userKeyHash_cookie_val)
                        # with the new cookie set, /welcome will do the auto login
                        self.redirect("/welcome")

                    # the username is already taken
                    else:
                        error = "Please choose a different username."
                        self.render("sign-up.html", error=error)
                # passwords DO NOT match
                else:
                    error2 = "Passwords must match."
                    self.render("sign-up.html", error=error)

            # if any field is not completed
            else:
                error = "Please complete all the fields"
                self.render("sign-up.html", error=error)
        except:
            error = "Error could not sign in. Could not access the database."
            self.render("sign-up.html", error=error)
