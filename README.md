
##Multi-user blog

Multi-user blog website built for google app engine in python and using datastore db.


### How to run:

The program can be run locally using gcloud local environment. 
From the command line at the root of the project dir: "dev_appserver.py .""  to run the local server on port 8080. 
Your datastore emulated db will store data locally and you can access the db console at port 8000.

To delpoy the app to the cloud: "gcloud app deploy --project NAME-ID"
then you can access the site via: "gcloud app browse" or just goto
https://APPNAMW-ID.appspot.com/

### Site functions:

The program will present the interface of a multi-user blog where users can post blogs, edit their own blogs, like other blogs, comment on other's blogs. User athentication is handled via cookies for return visitors with cookies enabled on their browswers. Passwords are hashed for security. Users are restricted from editing other's blogs or deleting others blogs. Users can like other's blogs but not their own.

