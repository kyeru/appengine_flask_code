from flask import flash, request, session
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
        return render_page('login.html')
    else:
        user_id = request.form['user_id']
        session['user_id'] = user_id
        flash('welcome %s.' % user_id)
        return redirect(url_for('default_page'))

def logout_page():
    user_id = get_user_id()
    if user_id != None:
        flash('bye, %s.' % user_id)
        session.pop('user_id')
    return redirect(url_for('default_page'))
