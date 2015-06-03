from flask import Flask, url_for, request
from google.appengine.ext import ndb
import cgi
import urllib2
from pageparser import *

app = Flask(__name__)
app.Debug = True

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

@app.route('/write/<word>/')
def write_data(word):
    counter = Counter.query(ancestor=ndb.Key(GroupType, 'WordBook'))
    if counter.count() == 0:
        new_counter = Counter(count=0)
        new_counter.Key = ndb.Key(
            Counter, 'counter', parent=ndb.Key(GroupType, 'WordBook'))
        new_counter.put()
    
    stored_entities = Word.query(Word.word == word)
    if stored_entities.count() == 0:
        counter = Counter.query(ancestor=ndb.Key(GroupType, 'WordBook'))
        count = 0
        for c in counter:
            c.count += 1
            count = c.count
            c.put()
        definition = get_word_definition(word)
        entity = Word(word=word,
                      num_id = count,
                      definition = definition)
        entity.Key = ndb.Key(
            Word, word, parent=ndb.Key(GroupType, 'WordBook'))
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
    #indexes = 
    #entities = Word.query(Word.word == word)
    return ''

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
