from google.appengine.ext import ndb

class NDBIException(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return '[NDBIException] ' + self.message

def make_ndb_filter(model, props):
    if len(props) == 0:
        raise NDBIException('filter property is empty')

    prop_list = list(props.iteritems())
    attr, value = prop_list[0]
    attribute = type(model).__getattribute__(model, attr)
    if len(props) == 1:
        return ndb.AND(attribute == value)
    else:
        return ndb.AND(attribute == value,
                       make_ndb_filter(model, dict(prop_list[1:])))

def read_entities(model, max_count, *args, **props):
    query = type(model).__getattribute__(model, 'query')

    ancestor_key = None
    if props.has_key('ancestor'):
        ancestor_key = props['ancestor']
        props.pop('ancestor')
    sort = None
    if props.has_key('sort'):
        sort = props['sort']
        props.pop('sort')
    sort_asc = False
    if props.has_key('asc'):
        sort_asc = props['asc']
        props.pop('asc')
    ndb_filter = None
    if len(props) > 0:
        ndb_filter = make_ndb_filter(model, dict(props))

    entities = list()
    bound_query = None
    if ndb_filter != None:
        if ancestor_key != None:
            bound_query = query(ndb_filter,
                                *args,
                                ancestor = ancestor_key)
        else:
            bound_query = query(ndb_filter, *args)
    else:
        if ancestor_key != None:
            bound_query = query(*args,
                                ancestor = ancestor_key)
        else:
            bound_query = query(*args)

    if sort != None:
        sort_target = type(model).__getattribute__(model, sort)
        bound_query = bound_query.order(
            sort_target if sort_asc else -sort_target)

    entities = list(bound_query.iter())
    return entities[:max_count] if max_count > 0 else entities

#####################################################################
# CRUD operations
#####################################################################

def create_entity(model, **props):
    #if len(read_entities(model, 1, **props)) > 0:
    #    raise NDBIException(
    #        'Entity ' + str(model) + ' for ' + str(props) + ' exists.')
    if props.has_key('ancestor'):
        ancestor_key = props['ancestor']
        props.pop('ancestor')
        props['parent'] = ancestor_key
    entity = model(**props)
    entity.put()

def read_entity(model, *args, **props):
    result = read_entities(model, 1, *args, **props)
    if len(result) > 0:
        return result[0]
    else:
        raise NDBIException(
            'Entity ' + str(model) + ' for ' + str(props) + ' not found.')

def update_entity(model, **props):
    try:
        result = read_entity(model, **props)
        if len(result) > 0:
            if props.has_key('ancestor'):
                ancestor_key = props['ancestor']
                props.pop('ancestor')
                props['parent'] = ancestor_key
            target = result.key.get()
            target.populate(**props)
            target.put()
    except NDBIException as e:
        raise NDBIException('Update error: ' + str(e))

def delete_entity(model, **props):
    try:
        entity = read_entity(model, **props)
        entity.key.delete()
    except NDBIException as e:
        raise NDBIException('Delete error: ' + str(e))

#####################################################################
# unit test
#####################################################################

class TestUser(ndb.Model):
    name = ndb.StringProperty()

class TestModel(ndb.Model):
    field1 = ndb.IntegerProperty()
    field2 = ndb.StringProperty()

if __name__ == '__main__':
    user = TestUser(name = "test")
    create_entity(TestModel, user, field1 = 1, field2 = "2")
    result = read_entity(TestModel, user, field1 = 1)
    assert(result.field2 == "2")
    update_entity(TestModel, user, field1 = 1, field2 = "3")
    result = read_entity(TestModel, user, field1 = 1)
    assert(result.field2 == "3")
    delete_entity(TestModel, user, field1 = 1)
