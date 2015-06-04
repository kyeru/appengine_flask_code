from flask import Flask, url_for, request, render_template
from google.appengine.ext import ndb
import cgi
import urllib2
import random

from pageparser import *

app = Flask(__name__)
app.Debug = True

group_name = 'WordBook'

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

def make_stylesheet(path):
    style = '<link rel="stylesheet" type="text/css"'
    style += ' href="' + path + '">'
    return style

def make_link(filename, text):
    anchor = '<a href="'
    anchor += url_for('static', filename=filename)
    anchor += '">' + cgi.escape(text) + '</a>'
    return anchor

class GroupType(ndb.Model):
    group_type = ndb.StringProperty()
    entity_count = ndb.IntegerProperty()

class Counter(ndb.Model):
    name = ndb.StringProperty()
    count = ndb.IntegerProperty()

class Word(ndb.Model):
    word = ndb.StringProperty()
    num_id = ndb.IntegerProperty()
    definition = ndb.StringProperty()

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

def initiate_counter(group_name):
    counter = Counter.query(Counter.name == group_name)
    if counter.count() == 0:
        new_counter = Counter(name=group_name, count=0)
        new_counter.Key = ndb.Key(
            Counter, 'counter', parent=ndb.Key(GroupType, group_name))
        new_counter.put()
    else:
        for c in counter:
            c.count = 0
            c.put()

@app.route('/write/<word>/')
def write_data(word):
    global group_name
    
    stored_entities = Word.query(Word.word == word)
    if stored_entities.count() == 0:
        counter = Counter.query(Counter.name == group_name)
        if counter.count() == 0:
            return 'counter not initiated'
        num_id = 0
        for c in counter:
            c.count = c.count + 1
            num_id = c.count
            c.put()
        definition = get_word_definition(word)
        entity = Word(
            word=word, num_id=num_id, definition=definition)
        #entity.Key = ndb.Key(
        #    Word, word, parent=ndb.Key(GroupType, group_name))
        entity.put()
        return word + ' is stored'
    else:
        return word + ' is already stored.'
    
@app.route('/read/<word>/')
def read_data(word):
    entities = Word.query(Word.word == word)
    answer = ''
    for entity in entities:
        answer += entity.word + ': ' + entity.definition + '\n'
    if len(answer) == 0:
        answer = 'no entry'
    return answer

@app.route('/random/')
def read_random_data():
    counter = Counter.query(Counter.name == group_name)
    if counter.count() == 0:
        return 'counter not initiated'
    count = 0
    for c in counter:
        count = c.count
    if count == 0:
        return 'no entry'
    index = random.randint(1, count)
    entities = Word.query(Word.num_id == index)
    answer = 'found:\n'
    for entity in entities:
        answer += '\t' + entity.word + '/' + entity.definition
    return answer

@app.route('/rand/', methods=['GET', 'POST'])
def rw_random():
    if request.method == 'GET':
        value = request.args.get('key', '')
        return 'GET ' + value
    else:
        pass

@app.route('/tmpl/')
@app.route('/tmpl/<name>/')
def template_test(name=None):
    return render_template('hello.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

@app.errorhandler(500)
def internal_server_error(e):
    return 'Internal Server Error: ' + str(e)

# initiating counter
# warning: global statment is not executed until the first request is handled.
initiate_counter(group_name)
