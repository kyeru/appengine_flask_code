import random

from google.appengine.ext import ndb
from mymodules import ndbi
from mymodules.counter import *

class WordBookException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

group_name = 'WordBook'

class GroupType(ndb.Model):
    group_type = ndb.StringProperty()

class Counter(ndb.Model):
    name = ndb.StringProperty()
    count = ndb.IntegerProperty()

class WordDefinition(ndb.Model):
    num_id = ndb.IntegerProperty()
    word = ndb.StringProperty()
    definition = ndb.StringProperty()

def add_word_definition(word, definition):
    try:
        get_word_definition(word)
    except WordBookException:
        # OK, a new word. Move on.
        pass
    else:
        raise WordBookException('duplicate write for ' + word)

    word_count = increase_counter(group_name)
    word = WordDefinition(num_id = word_count,
                          word = word,
                          definition = definition)
    word.put()
    
def get_word_definition(word):
    word_entity = ndbi.read_entity(WordDefinition, {'word': word})
    return word_entity.definition

def get_word_by_id(num_id):
    entity = ndbi.read_entity(WordDefinition, {'num_id': num_id})
    return (entity.word, entity.definition)

def get_random_words(count = 1):
    indexes = random.sample(range(1, get_count(group_name)), count)
    return [get_word_by_id(i) for i in indexes]
