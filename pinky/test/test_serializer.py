from decimal import Decimal
from twisted.trial import unittest

from pinky.core.serializer.json_serializer import JSONSerializer
from pinky.core.serializer.msgpack_serializer import MSGPackSerializer


class TestJSONSerializer(unittest.TestCase):

    def test_encode(self):
        data = {
            'decimal': Decimal('10.00'),
            'string': 'some_string',
            'int': 1234
        }
        expected = (
            '{"int": 1234, "decimal": "10.00", "string": "some_string"}'
        )
        retval = JSONSerializer.dump(data)
        self.assertEqual(retval, expected)
        self.assertTrue(isinstance(retval, str))

    def test_decode(self):
        data = (
            '{"int": 1234, "decimal": "10.00", "string": "some_string"}'
        )
        expected = {
            'decimal': '10.00',
            'string': 'some_string',
            'int': 1234
        }
        retval = JSONSerializer.load(data)
        self.assertEqual(retval, expected)
        self.assertTrue(isinstance(retval, dict))

    def test_none(self):
        retval = JSONSerializer.load(None)
        self.assertEqual(retval, None)


class TestMSGPackSerializer(unittest.TestCase):

    def test_encode(self):
        data = {
            'string': 'some_string',
            'int': 1234
        }
        expected = (
            '\x82\xc4\x03int\xcd\x04\xd2\xc4\x06string\xc4\x0bsome_string'
        )
        retval = MSGPackSerializer.dump(data)
        self.assertEqual(retval, expected)
        self.assertTrue(isinstance(retval, str))

    def test_decode(self):
        data = (
            '\x82\xc4\x03int\xcd\x04\xd2\xc4\x06string\xc4\x0bsome_string'
        )
        expected = {
            'string': 'some_string',
            'int': 1234
        }
        retval = MSGPackSerializer.load(data)
        self.assertEqual(retval, expected)
        self.assertTrue(isinstance(retval, dict))

    def test_none(self):
        retval = JSONSerializer.load(None)
        self.assertEqual(retval, None)
