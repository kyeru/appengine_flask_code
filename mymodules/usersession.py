from flask import request
from google.appengine.ext import ndb
from mymodules.rendercommon import *

class User(ndb.Model):
    user_id = ndb.StringProperty()
    nickname = ndb.StringProperty()
    password = ndb.StringProperty()

class LoginException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return 'login: ' + self.message


# page rendering
def login_page():
    if request.method == 'GET':
        return render_template('login.html',
                               method_get = True,
                               style_url = style_url())
    else:
        return render_template('login.html',
                               method_post = True,
                               style_url = style_url())

