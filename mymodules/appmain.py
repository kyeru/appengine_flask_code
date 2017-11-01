from os import urandom
import datetime
import cgitb

from flask import Flask, request, session

from mymodules import admin
from mymodules import upload
from mymodules import quiz
from mymodules import renderer
from mymodules import usersession


app = Flask(__name__)
app.Debug = True
app.secret_key = urandom(24)
app.permanent_session_lifetime = datetime.timedelta(hours = 1)
cgitb.enable(format="html")


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


# class AppException(Exception):
#     def __init__(self, msg):
#         self.message = msg
    
#     def __str__(self):
#         return '[AppException] ' + self.message


def clear_quiz_session():
    if 'quiz_id' in session:
        session.pop('quiz_id')


#
# routing
#


# default empty page
@app.route('/')
def default():
    clear_quiz_session()
    return renderer.default_page()


# about
@app.route('/about/')
def about():
    clear_quiz_session()
    return renderer.render_page('about.html')


# login
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    clear_quiz_session()
    return usersession.login_page()


# logout
@app.route('/logout/')
def logout():
    clear_quiz_session()
    return usersession.logout_page()


# quiz data upload
@app.route('/upload/', methods = ['GET', 'POST'])
def upload_file():
    clear_quiz_session()
    if request.method == 'GET':
        return upload.quiz_file_upload()
    else:
        return upload.quiz_file_upload_result()


# Quiz list
@app.route('/quiz/')
def quiz_list():
    clear_quiz_session()
    return quiz.quiz_list()


# Quiz
@app.route('/quiz/<category>/', methods = ['GET', 'POST'])
def run_quiz(category):
    if request.method == 'GET':
        return quiz.show_question(category)
    else:
        return quiz.evaluate_result(category)


# Scores
@app.route('/scores/')
@app.route('/scores/<category>/')
def show_scores(category = None):
    clear_quiz_session()
    return quiz.show_scores(category)


# admin
@app.route('/admin/', methods = ['GET', 'POST'])
def admin_start():
    if request.method == 'GET':
        return admin.admin_board()
    else:
        return admin.admin_action()


# error handler
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return renderer.error_page(
        'Sorry, nothing at this URL', 'default')

@app.errorhandler(500)
def internal_server_error(e):
    return renderer.error_page(
        'Internal Server Error: ' + str(e), 'default')
