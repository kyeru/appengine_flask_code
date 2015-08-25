import random

from google.appengine.ext import ndb

from mymodules import ndbi
from mymodules import renderer
from mymodules.counter import *
#from mymodules.user import *

#####################################################################
# ndb schema
#####################################################################

class NameDef(ndb.Model):
    num_id = ndb.IntegerProperty()
    category = ndb.StringProperty()
    name = ndb.StringProperty()
    definition = ndb.StringProperty()

#####################################################################
# exception
#####################################################################

class NameDefException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return '[NameDefException] ' + self.message

#####################################################################
# class and functions
#####################################################################

def get_def_by_name(user, category, name):
    entity = ndbi.read_entity(NameDef,
                              ancestor = user,
                              category = category,
                              name = name)
    return entity.definition

def get_item_by_id(user, category, num_id):
    entity = ndbi.read_entity(NameDef,
                              ancestor = user,
                              category = category,
                              num_id = num_id)
    return (entity.name, entity.definition)

def get_random_items(user, category, count = 1):
    total_item_count = get_count(user, category)
    if count >= total_item_count:
        raise NameDefException('not enough records stored')
    indexes = random.sample(range(1, total_item_count), count)
    return [get_item_by_id(user, category, i) for i in indexes]

def add_item(user, category, name, definition):
    try:
        get_def_by_name(user, category, name)
    except ndbi.NDBIException:
        # OK, a new word. Move on.
        pass
    else:
        raise NameDefException('duplicate write for ' + name)

    item_count = increase_counter(user, category)
    ndbi.create_entity(NameDef,
                       parent = user,
                       category = category,
                       num_id = item_count,
                       name = name,
                       definition = definition)

#####################################################################
# page rendering
#####################################################################

def random_item():
    try:
        (name, definition) = get_random_items(1)[0]
        return renderer.render_page('name_def.html',
                                    name = name,
                                    definition = definition)
    except Exception as e:
        return renderer.error_page('random_item(): ' + str(e),
                                   'read_random_item')
