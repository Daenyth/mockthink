from pprint import pprint
import rethinkdb as r
from mockthink.db import MockThink, MockThinkConn

def real_stock_data_load(data, connection):
    for db in list(r.db_list().run(connection)):
        r.db_drop(db).run(connection)
    for db_name, db_data in data['dbs'].iteritems():
        r.db_create(db_name).run(connection)
        for table_name, table_data in db_data['tables'].iteritems():
            r.db(db_name).table_create(table_name).run(conn)
            r.db(db_name).table(table_name).insert(table_data)

def mock_stock_data_load(data, connection):
    connection.reset_data(data)

def load_stock_data(data, connection):
    if isinstance(connection, MockThinkConn):
        return mock_stock_data_load(data, connection)
    else:
        pass




TESTS = {}

def register_test(Constructor, class_name, tests):
    def test(connection):
        instance = Constructor()
        for one_test in tests:
            load_stock_data(instance.get_data(), connection)
            print '%s: %s' % (class_name, one_test)
            test_func = getattr(instance, one_test)
            test_func(connection)
    TESTS[class_name] = test

class Meta(type):
    def __new__(cls, name, bases, attrs):
        result = super(Meta, cls).__new__(cls, name, bases, attrs)
        tests = [name for name in attrs.keys() if 'test' in name]
        register_test(result, result.__name__, tests)
        return result

class Base(object):
    __metaclass__ = Meta

class MockTest(Base):
    def get_data(self):
        return {
            'dbs': {
                'default': {
                    'tables': {}
                }
            }
        }
    def assertEqual(self, x, y, msg=''):
        try:
            assert(x == y)
        except AssertionError as e:
            print 'AssertionError: expected %s to equal %s' % (x, y)
            raise e



def as_db_and_table(db_name, table_name, data):
    return {
        'dbs': {
            db_name: {
                'tables': {
                    table_name: data
                }
            }
        }
    }


class TestGetting(MockTest):
    def get_data(self):
        data = [
            {'id': 'joe-id', 'name': 'joe'},
            {'id': 'bob-id', 'name': 'bob'}
        ]
        return as_db_and_table('x', 'people', data)

    def test_get_one_by_id(self, conn):
        result = r.db('x').table('people').get('bob-id').run(conn)
        self.assertEqual({'id': 'bob-id', 'name': 'bob'}, result)




if __name__ == '__main__':
    think = MockThink(as_db_and_table('nothing', 'nothing', []))
    conn = think.get_conn()
    for test_name, test_fn in TESTS.iteritems():
        test_fn(conn)

