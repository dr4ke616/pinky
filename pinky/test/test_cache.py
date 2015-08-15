from twisted.trial import unittest
from pinky.core.cache import InMemoryCache


class TestInMemoryCache(unittest.TestCase):

    def assert_cache(self, cache):
        self.assertEqual(cache.get('some_key'), 'some_value')
        self.assertEqual(cache['some_key'], 'some_value')

    def test_set(self):
        c = InMemoryCache()
        c.set('some_key', 'some_value')
        self.assert_cache(c)

    def test_get(self):
        c = InMemoryCache()
        c.set('some_key', 'some_value')
        self.assertEqual(c.get('some_key'), 'some_value')
        self.assert_cache(c)

    def test_mget(self):
        c = InMemoryCache()
        c.set('some_key1', 'some_value1')
        c.set('some_key2', 'some_value2')
        c.set('some_key3', 'some_value3')

        values = c.mget(['some_key1', 'some_key2', 'some_key3'])
        self.assertEqual(values, ['some_value1', 'some_value2', 'some_value3'])

    def test_delete(self):
        c = InMemoryCache()
        c.set('some_key', 'some_value')
        self.assert_cache(c)
        c.delete('some_key')
        self.assertEqual(c.get('some_key'), None)

    def test_keys(self):
        c = InMemoryCache()
        c.set('some_key1', 'some_value1')
        c.set('some_key2', 'some_value2')
        c.set('some_key3', 'some_value3')

        values = c.keys('some_key*')
        self.assertEqual(values, ['some_key1', 'some_key3', 'some_key2'])
