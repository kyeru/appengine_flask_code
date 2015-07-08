from os import urandom

from flask import Flask, request, session

from mymodules import quiz
from mymodules import renderer
from mymodules import usersession
from mymodules import worddef

app = Flask(__name__)
app.Debug = True
app.secret_key = urandom(24)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

class AppException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return '[AppException] ' + self.message

# default empty page
@app.route('/')
def default():
    return renderer.default_page()

# signin
@app.route('/signin/', methods = ['GET', 'POST'])
def signin():
    return renderer.under_construction()

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
        return quiz.quiz_file_upload()
    else:
        return quiz.quiz_file_upload_result()

# quiz
@app.route('/quiz/', methods = ['GET', 'POST'])
def quiz_and_result():
    if request.method == 'GET':
        return quiz.quiz_input()
    else:
        return quiz.quiz_result()

@app.route('/quiz/grade/')
def quiz_grade():
    return quiz.print_grade()

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
def read_random_word():
    return worddef.random_word()

# unused
@app.route('/test/')
@app.route('/test/<something>/')
def test_page():
    page += '<body>'
    page += '<h1>App engine + Flask test</h1>'
    page += '<p>this is test paragraph</p>'
    page += '</body>'
    return page
