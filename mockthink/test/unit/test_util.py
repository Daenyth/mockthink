import mock
import unittest
from ... import util

class Util(unittest.TestCase):
    def test_curry2(self):
        fun = lambda x, y: x + y
        curried = util.curry2(fun)
        self.assertEqual(8, curried(5, 3))
        self.assertEqual(8, curried(5)(3))

    def test_curry3(self):
        fun = lambda x, y, z: x + y + z
        curried = util.curry3(fun)
        self.assertEqual(15, curried(3, 5, 7))
        self.assertEqual(15, curried(3, 5)(7))
        self.assertEqual(15, curried(3)(5, 7))
        self.assertEqual(15, curried(3)(5)(7))

    def test_extend(self):
        dict_1 = {'x': 'x1-val', 'y': 'y1-val'}
        dict_2 = {'x': 'x2-val', 'z': 'z2-val'}

        extended = util.extend(dict_1, dict_2)
        self.assertEqual({
            'x': 'x2-val',
            'y': 'y1-val',
            'z': 'z2-val'
        }, extended)

        self.assertEqual({
            'x': 'x1-val',
            'y': 'y1-val'
        }, dict_1)

        self.assertEqual({
            'x': 'x2-val',
            'z': 'z2-val'
        }, dict_2)

    def test_cat(self):
        list_1 = [1, 2, 3]
        list_2 = [7, 8, 9]
        result = util.cat(list_1, list_2)
        self.assertEqual([1, 2, 3, 7, 8, 9], result)
        self.assertEqual([1, 2, 3], list_1)
        self.assertEqual([7, 8, 9], list_2)


    def test_extend_with(self):
        with mock.patch('mockthink.util.extend') as extend:
            extend.return_value = 'EXTENDED'
            util.extend_with('X', 'Y')
            util.extend_with('X')('Y')

            extend.assert_has_calls([
                mock.call('Y', 'X'),
                mock.call('Y', 'X')
            ])

    def test_map_with(self):
        add_1 = lambda x: x + 1
        nums = [10, 20, 30]
        map_fn = util.map_with(add_1)
        self.assertEqual([11, 21, 31], util.map_with(add_1)(nums))
        self.assertEqual([11, 21, 31], util.map_with(add_1, nums))

    def test_has_attrs(self):
        thing1 = {'a': 'a-val', 'b': 'b-val'}
        thing2 = {'x': 'x-val'}
        self.assertTrue(util.has_attrs(['a'], thing1))
        self.assertTrue(util.has_attrs(['a', 'b'], thing1))
        self.assertFalse(util.has_attrs(['a'], thing2))
        self.assertFalse(util.has_attrs(['a', 'b'], thing2))

    def test_nth(self):
        nums = [10, 20, 30, 40, 50]
        self.assertEqual(20, util.nth(1)(nums))
        self.assertEqual(40, util.nth(3)(nums))

    def test_as_obj(self):
        expected = {
            'x': 'x-val',
            'y': 'y-val'
        }
        pairs = [
            ['x', 'x-val'],
            ['y', 'y-val']
        ]
        self.assertEqual(expected, util.as_obj(pairs))

    def test_without(self):
        obj = {
            'x': 'x-val',
            'y': 'y-val',
            'z': 'z-val'
        }
        self.assertEqual({
            'z': 'z-val'
        }, util.without(['x', 'y'], obj))

        self.assertEqual({
            'x': 'x-val',
            'y': 'y-val'
        }, util.without(['z'], obj))

    def test_pluck_with(self):
        obj = {
            'x': 'x-val',
            'y': 'y-val',
            'z': 'z-val'
        }
        self.assertEqual({
            'x': 'x-val',
        }, util.pluck_with('x')(obj))
        self.assertEqual({
            'x': 'x-val',
            'y': 'y-val',
        }, util.pluck_with('x', 'y')(obj))

    def test_pipeline(self):
        add_5 = lambda x: x + 5
        mul_2 = lambda x: x * 2

        self.assertEqual(24, util.pipeline(add_5, mul_2)(7))
        self.assertEqual(19, util.pipeline(mul_2, add_5)(7))

    def test_match_attrs_matching(self):
        to_match = {
            'x': 'good-x',
            'y': 'good-y'
        }
        good_test = {
            'x': 'good-x',
            'y': 'good-y',
            'z': 'good-z'
        }
        self.assertTrue(util.match_attrs(to_match, good_test))

    def test_match_attrs_not_matching(self):
        to_match = {
            'x': 'good-x',
            'y': 'good-y'
        }
        bad_test = {
            'x': 'good-x',
            'y': 'bad-y',
            'z': 'good-z'
        }
        self.assertFalse(util.match_attrs(to_match, bad_test))


    def test_match_attrs_missing_val(self):
        to_match = {
            'x': 'good-x',
            'y': 'good-y'
        }
        bad_test = {
            'x': 'good-x',
            'z': 'good-z'
        }
        self.assertFalse(util.match_attrs(to_match, bad_test))

    def test_getter_dict(self):
        a_dict = {
            'x': 'x-val'
        }
        self.assertEqual('x-val', util.getter('x')(a_dict))
        self.assertEqual(None, util.getter('y')(a_dict))

    def test_getter_obj(self):

        class Thing(object):
            def __init__(self, a_dict):
                for k, v in a_dict.iteritems():
                    setattr(self, k, v)

        thing = Thing({'x': 'x-val'})

        self.assertEqual('x-val', util.getter('x')(thing))
        self.assertEqual(None, util.getter('y')(thing))

