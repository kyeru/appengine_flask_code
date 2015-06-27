from flask import Flask, request, session
from os import urandom

from mymodules.quiz import *
from mymodules.rendercommon import *
from mymodules.worddef import *

app = Flask(__name__)
app.Debug = True
app.secret_key = urandom(24)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

class AppException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return 'main: ' + self.message

# default empty page
@app.route('/')
def default_page():
    return default_page()

# login
@app.route('/login/', methods=['GET', 'POST'])
def login():
    return 'login'

# quiz data upload
@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return quiz_file_upload()
    else:
        return quiz_file_upload_result()

# quiz
@app.route('/quiz/', methods=['GET', 'POST'])
@app.route('/quiz/<user>/', methods=['GET', 'POST'])
def quiz_and_result(user = None):
    if request.method == 'GET':
        return quiz_input(user)
    else:
        return quiz_result(user)

# error handler
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return error_page('Sorry, nothing at this URL', 'default_page')
    #return 'Sorry, nothing at this URL.', 404

@app.errorhandler(500)
def internal_server_error(e):
    return error_page('Internal Server Error: ' + str(e),
                      'default_page')
    #return 'Internal Server Error: ' + str(e)

# test
@app.route('/random/')
def read_random_data():
    return random_word()

# unused
@app.route('/test/')
@app.route('/test/<something>/')
def test_page():
    page += '<body>'
    page += '<h1>App engine + Flask test</h1>'
    page += '<p>this is test paragraph</p>'
    page += '</body>'
    return page
