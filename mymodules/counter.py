from google.appengine.ext import ndb

from mymodules import ndbi

class Counter(ndb.Model):
    name = ndb.StringProperty()
    count = ndb.IntegerProperty()

class CounterException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return '[CounterException] ' + self.message

def initiate_counter(user, name, overwrite = True):
    try:
        counter = ndbi.read_entity(
            Counter, ancestor = user, name = name)
        if overwrite:
            counter.count = 0
            counter.put()
    except ndbi.NDBIException:
        ndbi.create_entity(Counter,
                           ancestor = user,
                           name = name,
                           count = 0)

def get_count(user, name):
    counter = ndbi.read_entity(
        Counter, ancestor = user, name = name)
    return counter.count

def increase_counter(user, name):
    counter = ndbi.read_entity(
        Counter, ancestor = user, name = name)
    counter.count += 1
    counter.put()
    return counter.count
