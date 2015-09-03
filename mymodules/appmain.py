from os import urandom
import datetime

from flask import Flask, request, session

from mymodules import upload
from mymodules import quiz
from mymodules import renderer
from mymodules import usersession

app = Flask(__name__)
app.Debug = True
app.secret_key = urandom(24)
app.permanent_session_lifetime = datetime.timedelta(hours = 1)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

class AppException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return '[AppException] ' + self.message

#####################################################################
# routing
#####################################################################

# default empty page
@app.route('/')
def default():
    return renderer.default_page()

# signin
@app.route('/signin/', methods = ['GET', 'POST'])
def signin():
    return renderer.under_construction()

# about
@app.route('/about/')
def about():
    return renderer.render_page('about.html')

# login
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    return usersession.login_page()

# logout
@app.route('/logout/')
def logout():
    return usersession.logout_page()

# quiz data upload
@app.route('/upload/', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return upload.quiz_file_upload()
    else:
        return upload.quiz_file_upload_result()

# quiz
@app.route('/quiz/')
@app.route('/quiz/<category>/', methods = ['GET', 'POST'])
def quiz_start(category = None):
    if category == None:
        return quiz.quiz_map()
    else:
        if request.method == 'GET':
            return quiz.quiz_input(category)
        else:
            return quiz.evaluate_result(category)

@app.route('/grade/')
@app.route('/grade/<category>/')
def print_grade(category = None):
    return quiz.check_grade(category)

# error handler
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return renderer.error_page(
        'Sorry, nothing at this URL', 'default')
    #return 'Sorry, nothing at this URL.', 404

@app.errorhandler(500)
def internal_server_error(e):
    return renderer.error_page(
        'Internal Server Error: ' + str(e), 'default')
    #return 'Internal Server Error: ' + str(e)

# test
@app.route('/random/')
def read_random_item():
    return namedef.random_item()
