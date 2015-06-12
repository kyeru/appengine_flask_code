from google.appengine.ext import ndb
from mymodules import ndbi

class Counter(ndb.Model):
    name = ndb.StringProperty()
    count = ndb.IntegerProperty()

class CounterException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def initiate_counter(name):
    try:
        counter = ndbi.read_entity(Counter, {'name': name})
        counter.count = 0
        counter.put()
    except ndbi.NDBIException:
        counter = Counter(name = name,
                          count = 0)
        counter.put()

def get_count(name):
    counter = ndbi.read_entity(Counter, {'name': name})
    return counter.count

def increase_counter(name):
    counter = ndbi.read_entity(Counter, {'name': name})
    counter.count += 1
    counter.put()
    return counter.count

