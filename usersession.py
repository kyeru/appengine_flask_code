import time

from flask import flash, redirect, request, session, url_for
from google.appengine.ext import ndb

from mymodules import renderer
from mymodules.user import *

class LoginException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return '[LoginException] ' + self.message

def issafe(user_id):
    return user_id.isalnum()

#####################################################################
# page rendering
#####################################################################

def signin():
    if request.method == 'GET':
        return renderer.under_construction()
    else:
        return renderer.under_construction()

def login_page():
    if request.method == 'GET':
        return renderer.render_page('login.html')
    else:
        user_id = request.form['user_id'].strip()
        if issafe(user_id):
            if not user_exists(user_id):
                add_user(user_id)
                session['user_id'] = user_id
            else:
                session['user_id'] = user_id
            flash('Hello, %s.' % user_id)
        else:
            flash('Invalid id: %s.' % user_id)
        return redirect(url_for('default'))

def logout_page():
    user_id = get_user_id()
    if user_id != None:
        flash('Bye, %s.' % user_id)
        session.pop('user_id')
    return redirect(url_for('default'))
