from google.appengine.ext import ndb
import random

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

class CounterNotInitiated(Exception):
    def __str__(self):
        return 'Counter is not initiated.'

class EntityNotFound(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Entity for ' + self.name + ' not found.'

class DuplicateWrite(Exception):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return 'Duplicate write for ' + self.name + ' not allowed.'

def initiate_counter():
    counter = Counter(name = group_name,
                      count = 0)
    counter.put()

def access_counter(name):
    counter = Counter.query(Counter.name == name).iter()
    if counter.has_next():
        return counter.next()
    else:
        raise CounterNotInitiated

def get_count():
    counter = access_counter(group_name)
    return counter.count

def increase_count():
    counter = access_counter(group_name)
    counter.count += 1
    counter.put()
    return counter.count

def add_word_definition(word, definition):
    try:
        get_word_definition(word)
    except EntityNotFound:
        # OK, a new word. Move on.
        pass
    else:
        raise DuplicateWrite(word)

    word_count = increase_count()
    word = WordDefinition(num_id = word_count,
                          word = word,
                          definition = definition)
    word.put()
    
def get_word_definition(word):
    entities = WordDefinition.query(WordDefinition.word == word).iter()
    if entities.has_next():
        return entities.next().definition
    else:
        raise EntityNotFound(word)

def get_word_by_id(num_id):
    entities = WordDefinition.query(WordDefinition.num_id == num_id).iter()
    if entities.has_next():
        entity = entities.next()
        return (entity.word, entity.definition)
    else:
        raise EntityNotFound('id ' + num_id)

def get_random_words(count = 1):
    result = []
    indexes = random.sample(range(1, get_count()), count)
    for i in indexes:
        result.append(get_word_by_id(i))
    return result
