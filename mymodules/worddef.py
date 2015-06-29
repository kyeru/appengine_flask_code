import random

from google.appengine.ext import ndb
from mymodules import ndbi
from mymodules import renderer
from mymodules.counter import *

group_name = 'WordDef'

class WordDefException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'worddef: ' + self.message

class WordDef(ndb.Model):
    num_id = ndb.IntegerProperty()
    word = ndb.StringProperty()
    definition = ndb.StringProperty()

def get_definition(word):
    entity = ndbi.read_entity(WordDef, {'word': word})
    return entity.definition

def get_worddef_by_id(num_id):
    entity = ndbi.read_entity(WordDef, {'num_id': num_id})
    return (entity.word, entity.definition)

def get_random_words(count = 1):
    indexes = random.sample(range(1, get_count(group_name)), count)
    return [get_worddef_by_id(i) for i in indexes]

def add_worddef(word, definition):
    try:
        get_definition(word)
    except ndbi.NDBIException:
        # OK, a new word. Move on.
        pass
    else:
        raise WordDefException('duplicate write for ' + word)

    word_count = increase_counter(group_name)
    ndbi.add_entity(WordDef,
                    num_id = word_count,
                    word = word,
                    definition = definition)

# page rendering
def random_word():
    try:
        (word, definition) = get_random_words(1)[0]
        return renderer.render_page('word_def.html',
                                    word = word,
                                    definition = definition)
    except Exception as e:
        return renderer.error_page('random_word(): ' + str(e),
                                   'read_random_word')
