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
    return entities[:max_count]

def read_entity(model, *args, **props):
    result = read_entities(model, 1, *args, **props)
    if len(result) > 0:
        return result[0]
    else:
        raise NDBIException(
            'Entity ' + str(model) + ' for ' + str(props) + ' not found.')

def add_entity(model, **props):
    entity = model(**props)
    entity.put()

def delete_entity(model, **props):
    entity = read_entity(model, **props)
    entity.key.delete()
