import unittest
from zope.interface import verify

from pinky.lib.interfaces import ISerializer
from pinky.lib.serializer.json_serializer import JSONSerializer


class TestInterface(unittest.TestCase):

    def test_jsonserializer_interfaces(self):
        self.assertTrue(verify.verifyClass(ISerializer, JSONSerializer))
