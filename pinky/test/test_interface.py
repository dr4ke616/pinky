from zope.interface import verify
from twisted.trial import unittest

from pinky.node.server import NodeServer
from pinky.node.client import NodeClient
from pinky.core.cache import InMemoryCache
from pinky.broker.server import BrokerServer
from pinky.broker.client import BrokerClient
from pinky.core.serializer.json_serializer import JSONSerializer
from pinky.core.interfaces import ISerializer, IStorage, IResponse
from pinky.core.serializer.msgpack_serializer import MSGPackSerializer
from pinky.core.response import Success, InternalServerError, Forbidden, Fail


class TestInterface(unittest.TestCase):

    def test_jsonserializer_interfaces(self):
        self.assertTrue(verify.verifyClass(ISerializer, JSONSerializer))

    def test_msgpackserializer_interfaces(self):
        self.assertTrue(verify.verifyClass(ISerializer, MSGPackSerializer))

    def test_storage_interfaces(self):
        self.assertTrue(verify.verifyClass(IStorage, NodeServer))
        self.assertTrue(verify.verifyClass(IStorage, BrokerServer))

        self.assertTrue(verify.verifyClass(IStorage, NodeClient))
        self.assertTrue(verify.verifyClass(IStorage, BrokerClient))

        self.assertTrue(verify.verifyClass(IStorage, InMemoryCache))

    def test_response_interfaces(self):
        self.assertTrue(verify.verifyClass(IResponse, Fail))
        self.assertTrue(verify.verifyClass(IResponse, Success))
        self.assertTrue(verify.verifyClass(IResponse, Forbidden))
        self.assertTrue(verify.verifyClass(IResponse, InternalServerError))
