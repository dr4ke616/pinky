import unittest
from zope.interface import verify

from pinky.node.server import NodeServer
from pinky.core.cache import InMemoryCache
from pinky.broker.server import BrokerServer
from pinky.core.interfaces import ISerializer, IStorage
from pinky.core.serializer.json_serializer import JSONSerializer
from pinky.core.serializer.msgpack_serializer import MSGPackSerializer


class TestInterface(unittest.TestCase):

    def test_jsonserializer_interfaces(self):
        self.assertTrue(verify.verifyClass(ISerializer, JSONSerializer))

    def test_msgpackserializer_interfaces(self):
        self.assertTrue(verify.verifyClass(ISerializer, MSGPackSerializer))

    def test_storage_interfaces(self):
        self.assertTrue(verify.verifyClass(IStorage, NodeServer))
        self.assertTrue(verify.verifyClass(IStorage, BrokerServer))
        self.assertTrue(verify.verifyClass(IStorage, InMemoryCache))
