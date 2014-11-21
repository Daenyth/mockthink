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

    def assertEqUnordered(self, x, y, msg=''):
        return self.assertEqual(x, y, msg)

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

class TestFiltering(MockTest):
    def get_data(self):
        data = [
            {'id': 'joe-id', 'name': 'joe', 'age': 28},
            {'id': 'bob-id', 'name': 'bob', 'age': 19},
            {'id': 'bill-id', 'name': 'bill', 'age': 35},
            {'id': 'kimye-id', 'name': 'kimye', 'age': 17}
        ]
        return as_db_and_table('x', 'people', data)

    def test_filter_lambda_gt(self, conn):
        expected = [
            {'id': 'joe-id', 'name': 'joe', 'age': 28},
            {'id': 'bill-id', 'name': 'bill', 'age': 35}
        ]
        result = r.db('x').table('people').filter(lambda p: p['age'] > 20).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_filter_lambda_lt(self, conn):
        expected = [
            {'id': 'bob-id', 'name': 'bob', 'age': 19},
            {'id': 'kimye-id', 'name': 'kimye', 'age': 17}
        ]
        result = r.db('x').table('people').filter(lambda p: p['age'] < 20).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_filter_dict_match(self, conn):
        expected = [{'id': 'bill-id', 'name': 'bill', 'age': 35}]
        result = r.db('x').table('people').filter({'age': 35}).run(conn)
        self.assertEqual(expected, list(result))


class TestMapping(MockTest):
    def get_data(self):
        data = [
            {'id': 'joe-id', 'name': 'joe', 'age': 28},
            {'id': 'bob-id', 'name': 'bob', 'age': 19},
            {'id': 'bill-id', 'name': 'bill', 'age': 35},
            {'id': 'kimye-id', 'name': 'kimye', 'age': 17}
        ]
        return as_db_and_table('x', 'people', data)

    def test_map_gt(self, conn):
        expected = [
            True, False, True, False
        ]
        result = r.db('x').table('people').map(lambda p: p['age'] > 20).run(conn)
        self.assertEqual(expected, list(result))

class TestPlucking(MockTest):
    def get_data(self):
        data = [
            {'id': 'joe-id', 'name': 'joe', 'hobby': 'guitar'},
            {'id': 'bob-id', 'name': 'bob', 'hobby': 'pseudointellectualism'},
            {'id': 'bill-id', 'name': 'bill'},
            {'id': 'kimye-id', 'name': 'kimye', 'hobby': 'being kimye'}
        ]
        return as_db_and_table('x', 'people', data)

    def test_pluck_missing_attr(self, conn):
        expected = [
            {'id': 'joe-id', 'hobby': 'guitar'},
            {'id': 'bob-id', 'hobby': 'pseudointellectualism'},
            {'id': 'bill-id'},
            {'id': 'kimye-id', 'hobby': 'being kimye'}
        ]
        result = r.db('x').table('people').pluck('id', 'hobby').run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_pluck_missing_attr_list(self, conn):
        expected = [
            {'id': 'joe-id', 'hobby': 'guitar'},
            {'id': 'bob-id', 'hobby': 'pseudointellectualism'},
            {'id': 'bill-id'},
            {'id': 'kimye-id', 'hobby': 'being kimye'}
        ]
        result = r.db('x').table('people').pluck(['id', 'hobby']).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_sub_pluck(self, conn):
        expected = [
            {'id': 'joe-id', 'hobby': 'guitar'},
            {'id': 'bob-id', 'hobby': 'pseudointellectualism'},
            {'id': 'bill-id'},
            {'id': 'kimye-id', 'hobby': 'being kimye'}
        ]
        result = r.db('x').table('people').map(lambda p: p.pluck('id', 'hobby')).run(conn)
        self.assertEqUnordered(expected, list(result))


class TestPlucking2(MockTest):
    def get_data(self):
        data = [
            {
                'id': 'thing-1',
                'values': {
                    'a': 'a-1',
                    'b': 'b-1',
                    'c': 'c-1',
                    'd': 'd-1'
                }
            },
            {
                'id': 'thing-2',
                'values': {
                    'a': 'a-2',
                    'b': 'b-2',
                    'c': 'c-2',
                    'd': 'd-2'
                }
            },
        ]
        return as_db_and_table('some-db', 'things', data)

    def test_sub_sub(self, conn):
        expected = [
            {'a': 'a-1', 'd': 'd-1'},
            {'a': 'a-2', 'd': 'd-2'}
        ]
        result = r.db('some-db').table('things').map(lambda t: t['values'].pluck('a', 'd')).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_sub_sub_list(self, conn):
        expected = [
            {'a': 'a-1', 'd': 'd-1'},
            {'a': 'a-2', 'd': 'd-2'}
        ]
        result = r.db('some-db').table('things').map(lambda t: t['values'].pluck('a', 'd')).run(conn)
        self.assertEqUnordered(expected, list(result))



class TestWithout(MockTest):
    def get_data(self):
        data = [
            {'id': 'joe-id', 'name': 'joe', 'hobby': 'guitar'},
            {'id': 'bob-id', 'name': 'bob', 'hobby': 'pseudointellectualism'},
            {'id': 'bill-id', 'name': 'bill'},
            {'id': 'kimye-id', 'name': 'kimye', 'hobby': 'being kimye'}
        ]
        return as_db_and_table('x', 'people', data)

    def test_without_missing_attr(self, conn):
        expected = [
            {'id': 'joe-id'},
            {'id': 'bob-id'},
            {'id': 'bill-id'},
            {'id': 'kimye-id'}
        ]
        result = r.db('x').table('people').without('name', 'hobby').run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_without_missing_attr_list(self, conn):
        expected = [
            {'id': 'joe-id'},
            {'id': 'bob-id'},
            {'id': 'bill-id'},
            {'id': 'kimye-id'}
        ]
        result = r.db('x').table('people').without(['name', 'hobby']).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_sub_without(self, conn):
        expected = [
            {'id': 'joe-id'},
            {'id': 'bob-id'},
            {'id': 'bill-id'},
            {'id': 'kimye-id'}
        ]
        result = r.db('x').table('people').map(lambda p: p.without('name', 'hobby')).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_sub_without_list(self, conn):
        expected = [
            {'id': 'joe-id'},
            {'id': 'bob-id'},
            {'id': 'bill-id'},
            {'id': 'kimye-id'}
        ]
        result = r.db('x').table('people').map(lambda p: p.without(['name', 'hobby'])).run(conn)
        self.assertEqUnordered(expected, list(result))

class TestWithout2(MockTest):
    def get_data(self):
        data = [
            {
                'id': 'thing-1',
                'values': {
                    'a': 'a-1',
                    'b': 'b-1',
                    'c': 'c-1',
                    'd': 'd-1'
                }
            },
            {
                'id': 'thing-2',
                'values': {
                    'a': 'a-2',
                    'b': 'b-2',
                    'c': 'c-2',
                    'd': 'd-2'
                }
            },
        ]
        return as_db_and_table('some-db', 'things', data)

    def test_sub_sub(self, conn):
        expected = [
            {'b': 'b-1', 'c': 'c-1'},
            {'b': 'b-2', 'c': 'c-2'}
        ]
        result = r.db('some-db').table('things').map(lambda t: t['values'].without('a', 'd')).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_sub_sub_list(self, conn):
        expected = [
            {'b': 'b-1', 'c': 'c-1'},
            {'b': 'b-2', 'c': 'c-2'}
        ]
        result = r.db('some-db').table('things').map(lambda t: t['values'].without(['a', 'd'])).run(conn)
        self.assertEqUnordered(expected, list(result))


class TestBracket(MockTest):
    def get_data(self):
        data = [
            {
                'id': 'thing-1',
                'other_val': 'other-1',
                'values': {
                    'a': 'a-1',
                    'b': 'b-1',
                    'c': 'c-1',
                    'd': 'd-1'
                }
            },
            {
                'id': 'thing-2',
                'other_val': 'other-2',
                'values': {
                    'a': 'a-2',
                    'b': 'b-2',
                    'c': 'c-2',
                    'd': 'd-2'
                }
            },
        ]
        return as_db_and_table('some-db', 'things', data)

    def test_one_level(self, conn):
        expected = ['other-1', 'other-2']
        result = r.db('some-db').table('things').map(lambda t: t['other_val']).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_nested(self, conn):
        expected = ['c-1', 'c-2']
        result = r.db('some-db').table('things').map(lambda t: t['values']['c']).run(conn)
        self.assertEqUnordered(expected, list(result))

class TestMath(MockTest):
    def get_data(self):
        data = [
            {
                'id': 'pt-1',
                'x': 10,
                'y': 25
            },
            {
                'id': 'pt-2',
                'x': 100,
                'y': 3
            }
        ]
        return as_db_and_table('math-db', 'points', data)

    def test_add_method(self, conn):
        expected = [35, 103]
        result = r.db('math-db').table('points').map(lambda t: t['x'].add(t['y'])).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_add_oper(self, conn):
        expected = [35, 103]
        result = r.db('math-db').table('points').map(lambda t: t['x'] + t['y']).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_sub_method(self, conn):
        expected = [-15, 97]
        result = r.db('math-db').table('points').map(lambda t: t['x'].sub(t['y'])).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_sub_oper(self, conn):
        expected = [-15, 97]
        result = r.db('math-db').table('points').map(lambda t: t['x'] - t['y']).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_mul_method(self, conn):
        expected = [250, 300]
        result = r.db('math-db').table('points').map(lambda t: t['x'].mul(t['y'])).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_mul_oper(self, conn):
        expected = [250, 300]
        result = r.db('math-db').table('points').map(lambda t: t['x'] * t['y']).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_div_method(self, conn):
        expected = [250, 300]
        result = r.db('math-db').table('points').map(lambda t: t['x'].mul(t['y'])).run(conn)
        self.assertEqUnordered(expected, list(result))

    def test_mul_oper(self, conn):
        expected = [250, 300]
        result = r.db('math-db').table('points').map(lambda t: t['x'] * t['y']).run(conn)
        self.assertEqUnordered(expected, list(result))



class TestUpdating(MockTest):
    def get_data(self):
        data = [
            {'id': 'kermit-id', 'species': 'frog', 'name': 'Kermit'},
            {'id': 'piggy-id', 'species': 'pig', 'name': 'Ms. Piggy'}
        ]
        return as_db_and_table('things', 'muppets', data)

    def test_update_one(self, conn):
        expected = {'id': 'kermit-id', 'species': 'green frog', 'name': 'Kermit'}
        r.db('things').table('muppets').get('kermit-id').update({'species': 'green frog'}).run(conn)
        result = r.db('things').table('muppets').get('kermit-id').run(conn)
        self.assertEqual(expected, result)

    def test_update_sequence(self, conn):
        expected = [
            {'id': 'kermit-id', 'species': 'frog', 'name': 'Kermit', 'is_muppet': 'very'},
            {'id': 'piggy-id', 'species': 'pig', 'name': 'Ms. Piggy', 'is_muppet': 'very'}
        ]
        r.db('things').table('muppets').update({'is_muppet': 'very'}).run(conn)
        result = r.db('things').table('muppets').run(conn)
        self.assertEqual(expected, list(result))


def common_join_data():
    people_data = [
        {'id': 'joe-id', 'name': 'Joe'},
        {'id': 'tom-id', 'name': 'Tom'},
        {'id': 'arnold-id', 'name': 'Arnold'}
    ]
    job_data = [
        {'id': 'lawyer-id', 'name': 'Lawyer'},
        {'id': 'nurse-id', 'name': 'Nurse'},
        {'id': 'semipro-wombat-id', 'name': 'Semi-Professional Wombat'}
    ]
    employee_data = [
        {'id': 'joe-emp-id', 'person': 'joe-id', 'job': 'lawyer-id'},
        {'id': 'arnold-emp-id', 'person': 'arnold-id', 'job': 'nurse-id'}
    ]
    data = {
        'dbs': {
            'jezebel': {
                'tables': {
                    'people': people_data,
                    'jobs': job_data,
                    'employees': employee_data
                }
            }
        }

    }
    return data

class Test_Eq_Join(MockTest):
    def get_data(self):
        return common_join_data()

    def test_eq_join_1(self, conn):
        expected = [
            {
                'left': {
                    'id': 'joe-emp-id',
                    'person': 'joe-id',
                    'job': 'lawyer-id'
                },
                'right': {
                    'id': 'joe-id',
                    'name': 'Joe'
                }
            },
            {
                'left': {
                    'id': 'arnold-emp-id',
                    'person': 'arnold-id',
                    'job': 'nurse-id'
                },
                'right': {
                    'id': 'arnold-id',
                    'name': 'Arnold'
                }
            }
        ]
        result = r.db('jezebel').table('employees').eq_join('person', r.db('jezebel').table('people')).run(conn)
        self.assertEqUnordered(expected, list(result))



if __name__ == '__main__':
    think = MockThink(as_db_and_table('nothing', 'nothing', []))
    conn = think.get_conn()
    for test_name, test_fn in TESTS.iteritems():
        test_fn(conn)

