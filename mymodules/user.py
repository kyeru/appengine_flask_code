from flask import session
from google.appengine.ext import ndb

class User(ndb.Model):
    user_id = ndb.StringProperty()
    password = ndb.StringProperty()

def get_user_id():
    if 'user_id' in session:
        return session['user_id']
    else:
        return None
