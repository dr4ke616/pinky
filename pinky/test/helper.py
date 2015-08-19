import json
from mock import patch
from twisted.trial import unittest
from txzmq import ZmqEndpoint, ZmqFactory


class MockJSONSerializer(object):
    """ Mock JSON serializer. Just used to json encode and decode
        for various test cases
    """

    @classmethod
    def dump(cls, content):
        if content is not None:
            return json.dumps(content)

    @classmethod
    def load(cls, content):
        if content is not None:
            return json.loads(content)


class MockBaseServer(object):

    __serializer__ = MockJSONSerializer
    _debug = False

    def __init__(self, factory, endpoint, *args, **kwargs):
        self.factory = factory
        self.endpoints = [endpoint]

    def shutdown(self):
        pass

    @classmethod
    def create(cls, address, *args, **kwargs):
        return cls(
            ZmqFactory(), ZmqEndpoint('bind', address), *args, **kwargs
        )


class BaseTestServer(unittest.TestCase):

    server = None

    def __init__(self, *args, **kwargs):
        self.patchs = [
            patch.object(self.server, '__bases__', (MockBaseServer, ))
        ]
        super(BaseTestServer, self).__init__(*args, **kwargs)

    def add_patch(self, patch):
        self.patchs.append(patch)

    def setUp(self):
        [p.start() for p in self.patchs]

    def tearDown(self):
        try:
            [p.stop() for p in self.patchs]
        except:
            pass
