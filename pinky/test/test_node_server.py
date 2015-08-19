from mock import patch, Mock

from twisted.internet import defer

from pinky.core.response import Success
from pinky.node.server import NodeServer
from pinky.core.cache import InMemoryCache
from helper import BaseTestServer, MockJSONSerializer, ZmqEndpoint, ZmqFactory

ADDRESS = 'tcp://127.0.0.1:42000'


class MockUUID(object):

    @staticmethod
    def uuid4():
        return 'mock_id'


class MockBroker(Mock):

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def shutdown(self):
        pass

    def register_node(self, *args, **kwargs):
        return defer.succeed({'message': None, 'success': True})


class TestNodeServer(BaseTestServer):

    server = NodeServer

    def __init__(self, *args, **kwargs):
        super(TestNodeServer, self).__init__(*args, **kwargs)
        self.add_patch(patch('pinky.node.server.uuid', MockUUID))

    def test_create(self):
        allowed_methods = (
            'ping', 'set', 'get', 'mget', 'delete',
            'keys', 'sync', 'take_snapshot'
        )
        server = NodeServer.create(ADDRESS)
        self.assertEqual(server.__allowed_methods__, allowed_methods)
        self.assertEqual(server.__serializer__, MockJSONSerializer)
        self.assertIsInstance(server.factory, ZmqFactory)
        self.assertIsInstance(server.endpoints[0], ZmqEndpoint)
        self.assertEqual(server._address, ADDRESS)
        self.assertFalse(server._is_registered)
        self.assertEqual(type(server._cache_class), InMemoryCache)
        server.shutdown()

    def test_generate_id(self):
        node = NodeServer(ZmqFactory(), ZmqEndpoint('bind', ADDRESS))
        self.assertEqual(node.id, 'mock_id')
        self.assertEqual(node.id, 'mock_id')

    def test_register_with_broker(self):

        node = NodeServer.create(ADDRESS)
        d = node.register_with_broker(MockBroker(), 'some_address')
        d.addCallback(lambda _: self.assertTrue(node._is_registered))
        return d

    def test_register_with_broker_fail(self):
        class _MockBroker(MockBroker):
            def register_node(self, *args, **kwargs):
                return defer.succeed(
                    {'message': 'dummy_error', 'success': False}
                )

        err_back = Mock(
            side_affect=lambda: defer.succeed(None),
            return_value=defer.succeed(None)
        )

        node = NodeServer.create(ADDRESS)
        d = node.register_with_broker(_MockBroker(), 'some_address')
        d.addErrback(err_back)
        d.addCallback(lambda _: self.assertFalse(node._is_registered))
        d.addCallback(lambda _: self.assertTrue(err_back.called))
        return d

    def test_ping(self):
        node = NodeServer.create(ADDRESS)
        self.assertIsInstance(node.ping(), Success)

    def test_sync(self):
        node = NodeServer.create(ADDRESS)
        node.sync({'some_key': 'some_value'})
        self.assertEqual(node._cache_class, {'some_key': 'some_value'})

    def test_take_snapshot(self):
        node = NodeServer.create(ADDRESS)
        node.sync({'some_key': 'some_value'})
        response = node.take_snapshot()
        self.assertTrue(response.success)
        self.assertIsInstance(response, Success)
        self.assertEqual(response.message, {'some_key': 'some_value'})

    def _validate_operation_response(self, response, expected_message):
        self.assertTrue(response.success)
        self.assertIsInstance(response, Success)
        self.assertEqual(response.message, expected_message)

    def test_set(self):
        node = NodeServer.create(ADDRESS)
        response = node.set(key='some_key', value='some_value')
        self._validate_operation_response(response, None)
        self.assertEqual(node._cache_class, {'some_key': 'some_value'})

    def test_get(self):
        node = NodeServer.create(ADDRESS)
        node.set(key='some_key', value='some_value')
        self.assertEqual(node._cache_class, {'some_key': 'some_value'})

        response = node.get(key='some_key')
        self._validate_operation_response(response, 'some_value')

    def test_mget(self):
        node = NodeServer.create(ADDRESS)
        node.set(key='some_key1', value='some_value1')
        node.set(key='some_key2', value='some_value2')
        self.assertEqual(
            node._cache_class,
            {'some_key1': 'some_value1', 'some_key2': 'some_value2'}
        )

        response = node.mget(keys=['some_key1', 'some_key2'])
        self._validate_operation_response(
            response, ['some_value1', 'some_value2']
        )

    def test_delete(self):
        node = NodeServer.create(ADDRESS)
        node.set(key='some_key', value='some_value')
        self.assertEqual(node._cache_class, {'some_key': 'some_value'})

        response = node.delete(key='some_key')
        self._validate_operation_response(response, None)
        self.assertEqual(node._cache_class, {})

    def test_keys(self):
        node = NodeServer.create(ADDRESS)
        node.set(key='some_key1', value='some_value1')
        node.set(key='some_key2', value='some_value2')
        self.assertEqual(
            node._cache_class,
            {'some_key1': 'some_value1', 'some_key2': 'some_value2'}
        )

        response = node.keys(pattern='some_key*')
        self._validate_operation_response(
            response, ['some_key1', 'some_key2']
        )
