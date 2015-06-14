from flask import Flask, url_for, redirect, request
from flask import render_template, session
import cgi
from os import urandom

from mymodules.counter import *
from mymodules.fileparser import *
from mymodules.pageparser import fetch_definition
from mymodules.quiz import *
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
        return self.message

# style
def style_url():
    return url_for('static', filename = 'style.css')

# counter reset
@app.route('/init/')
def initiate():
    initiate_counter('QuizSeqNum')
    return 'Initiated.'

# entity upload
@app.route('/write/<word>/')
def write_data(word):
    ''' Adds a single word definition to the datastore '''
    try:
        add_worddef(word, fetch_definition(word))
        return word + ' is stored'
    except Exception as e:
        return str(e)
    
@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    ''' Uploads a quiz input file. '''
    if request.method == 'GET':
        return render_template(
            'file_upload.html',
            style_url = style_url)
    else:
        f = request.files['the_file']
        try:
            result = parse_file(f)
            for (word, definition) in result:
                add_worddef(word, definition)
            return str(len(result)) + ' words stored'
        except Exception as e:
            return str(e)
# quiz
def quiz_input():
    try:
        seqno = int(request.args.get('seqno', ''))
        content = get_random_words(4)
        answer = random.randint(0, len(content) - 1) + 1
        qna = QuestionAnswer(content, answer)
        target, choices = QuizGenerator.translate(qna, seqno)
        numbered_choices = []
        for choice in choices:
            numbered_choices.append({'num': len(numbered_choices) + 1,
                                     'text': choice})
        return render_template('quiz.html',
                               style_url = style_url(),
                               target = target,
                               choices = numbered_choices)
    except Exception:
        return redirect(url_for('quiz_and_result',
                                seqno = get_quiz_seqno()))

def quiz_result():
    try:
        seqno = int(request.args.get('seqno', ''))
        user_answer = request.form['choice']
        qna = QuizGenerator.load(seqno)
        QuizGenerator.cleanup(seqno)
        return render_template('quiz_result.html',
                               style_url = style_url(),
                               result = qna.evaluate(int(user_answer)),
                               answer = qna.answer,
                               next_url = url_for('quiz_and_result'))
    except Exception as e:
        return render_template('quiz_error.html',
                               style_url = style_url(),
                               message = str(e),
                               next_url = url_for('quiz_and_result'))

@app.route('/quiz/', methods=['GET', 'POST'])
def quiz_and_result():
    if request.method == 'GET':
        return quiz_input()
    else:
        return quiz_result()

# error handler
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

@app.errorhandler(500)
def internal_server_error(e):
    return 'Internal Server Error: ' + str(e)

# test
@app.route('/random/')
def read_random_data():
    try:
        (word, definition) = get_random_words(1)[0]
        return render_template('word_def.html',
                               style_url = style_url(),
                               word = word,
                               definition = definition)
    except Exception as e:
        return str(e)

@app.route('/unit/')
def unittest():
    try:
        counter = get_count('WordBook')
        return str(count)
    except Exception as e:
        return str(e)

#
# Unused: Just for practice
#
def make_stylesheet(path):
    style = '<link rel="stylesheet" type="text/css"'
    style += ' href="' + path + '">'
    return style

def make_link(filename, text):
    anchor = '<a href="'
    anchor += url_for('static', filename=filename)
    anchor += '">' + cgi.escape(text) + '</a>'
    return anchor

@app.route('/test/')
def test_page():
    header = '<head>'
    header += make_stylesheet(url_for('static', filename='style.css'))
    header += '</head>'

    page = header
    page += '<body>'
    page += '<h1>App engine + Flask test</h1>'
    page += '<p>this is test paragraph</p>'
    page += make_link('test.html', 'test')
    page += '</body>'
    return page

@app.route('/tmpl/')
@app.route('/tmpl/<name>/')
def template_test(name=None):
    return render_template('hello.html', name=name)
