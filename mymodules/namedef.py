import random

from google.appengine.ext import ndb

from mymodules import ndbi
from mymodules import renderer
from mymodules.counter import *


#
# ndb schema
#

class Category(ndb.Model):
    # parent: user key
    name = ndb.StringProperty()
    item_count = ndb.IntegerProperty()


class Item(ndb.Model):
    # parent: category key
    number = ndb.IntegerProperty()
    name = ndb.StringProperty()
    description = ndb.StringProperty()


#
# exception
#

# class ItemException(Exception):
#     def __init__(self, message):
#         self.message = message

#     def __str__(self):
#         return '[ItemException] ' + self.message


def category_key(category):
    return ndb.Key(Category, category)

#
# Read and write items
#


def get_item_by_name(user, category, name):
    item = ndbi.read(Item,
                     ancestor = category_key(category),
                     name = name)
    if item == None:
        raise Exception('No item "' + name + '" exists.')
    return item.description


def get_item_by_number(user, category, number):
    item = ndbi.read(Item,
                     ancestor = category_key(category),
                     number = number)
    if item == None:
        raise Exception('No item number "' + str(number) + '" exists.')
    return (item.name, item.description)


def get_random_items(user, category, count):
    total_count = ndbi.read(Category, name = category).item_count
    if count >= total_count:
        raise Exception('Not enough records stored')
    indexes = random.sample(range(1, total_count), count)
    return [get_item_by_number(user, category, i) for i in indexes]


def add_item(user, category, name, description):
    item = ndbi.read(Item,
                     ancestor = category_key(category),
                     name = name)
    if item == None:
        c = ndbi.read(Category, name = category)
        c.item_count += 1
        item_count = c.item_count
        c.put()
        ndbi.create(Item,
                    ancestor = category_key(category),
                    number = item_count,
                    name = name,
                    description = description)
    else:
        raise Exception('Duplicate write for ' + name)
