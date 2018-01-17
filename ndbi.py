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
    parent = None
    if props.has_key('ancestor'):
        parent = props['ancestor']
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

    bound_query = None
    if ndb_filter != None:
        if parent != None:
            bound_query = model.query(ndb_filter,
                                      *args,
                                      ancestor = parent)
        else:
            bound_query = model.query(ndb_filter, *args)
    else:
        if parent != None:
            bound_query = model.query(*args, ancestor = parent)
        else:
            bound_query = model.query(*args)

    if sort != None:
        sort_target = type(model).__getattribute__(model, sort)
        bound_query = bound_query.order(
            sort_target if sort_asc else -sort_target)

    entities = list(bound_query.iter())
    return entities[:max_count] if max_count > 0 else entities


#
# CRUD operations
#


def create(model, **props):
    #if len(read_entities(model, 1, **props)) > 0:
    #    raise NDBIException(
    #        'Entity ' + str(model) + ' for ' + str(props) + ' exists.')
    if props.has_key('ancestor'):
        parent = props['ancestor']
        props.pop('ancestor')
        props['parent'] = parent
    entity = model(**props)
    entity.put()


def read(model, *args, **props):
    result = read_entities(model, 1, *args, **props)
    if len(result) > 0:
        return result[0]
    else:
        return None


def update(entity, model, **props):
    if props.has_key('ancestor'):
        parent = props['ancestor']
        props.pop('ancestor')
        props['parent'] = parent
    target = entity.key.get()
    target.populate(**props)
    target.put()


def delete(model, **props):
    target = read(model, **props)
    if target == None:
        raise NDBIException(
            'Delete error: ' + str(model) + ' ' + str(props) + ' not exists.')
    target.key.delete()


def delete_all(model, **props):
    targets = read_entities(model, 0, **props)
    ndb.delete_multi([target.key for target in targets])


#
# unit test
#


class TestUser(ndb.Model):
    name = ndb.StringProperty()


class TestModel(ndb.Model):
    field1 = ndb.IntegerProperty()
    field2 = ndb.StringProperty()


if __name__ == '__main__':
    user = TestUser(name = "test")
    create(TestModel, ancestor = user, field1 = 1, field2 = "2")
    result = read(TestModel, ancestor = user, field1 = 1)
    assert(result.field2 == "2")
    update(TestModel, ancestor = user, field1 = 1, field2 = "3")
    result = read(TestModel, ancestor = user, field1 = 1)
    assert(result.field2 == "3")
    delete(TestModel, ancestor = user, field1 = 1)
    create(TestModel, ancestor = user, field1 = 2)
    create(TestModel, ancestor = user, field1 = 3)
    delete_all(TestModel, ancestor = user)
    result = read_entities(TestModel, ancestor = user)
    assert(len(result) == 0)    