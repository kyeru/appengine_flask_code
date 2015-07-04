from google.appengine.ext import ndb

class NDBIException(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return 'NDBIException(' + self.message + ')'

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

def read_entities(model, max_count, **props):
    query = type(model).__getattribute__(model, 'query')
    if props.has_key('ancestor'):
        ancestor_key = props['ancestor']
        props.pop('ancestor')
        ndb_filter = make_ndb_filter(model, dict(props))
        entities = list(query(ndb_filter, ancestor = ancestor_key).iter())
        return entities[:max_count]
    else:
        ndb_filter = make_ndb_filter(model, dict(props))
        entities = list(query(ndb_filter).iter())
        return entities[:max_count]

def read_entity(model, **props):
    result = read_entities(model, 1, **props)
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
