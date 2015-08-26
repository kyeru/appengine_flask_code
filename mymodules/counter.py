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
    counter = ndbi.read(Counter, ancestor = user, name = name)
    if counter == None:
        ndbi.create(Counter, ancestor = user, name = name, count = 0)
    else:
        if overwrite:
            counter.count = 0
            counter.put()

def get_count(user, name):
    counter = ndbi.read(Counter, ancestor = user, name = name)
    if counter == None:
        raise CounterException('Counter "' + name + '" not exists.')
    return counter.count

def increase_counter(user, name):
    counter = ndbi.read(Counter, ancestor = user, name = name)
    if counter == None:
        raise CounterException('Counter "' + name + '" not exists.')
    counter.count += 1
    counter.put()
    return counter.count
