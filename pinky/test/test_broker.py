import json

from mock import Mock, patch
from twisted.trial import unittest
from twisted.internet import defer
from txzmq import ZmqEndpoint, ZmqFactory

from pinky.core.response import Success
from pinky.node.client import NodeClient
from pinky.core.hash import ConsistentHash
from pinky.core.exceptions import ZeroNodes
from pinky.broker.server import BrokerServer

ADDRESS = 'tcp://127.0.0.1:42000'


class MockLoopingCall(Mock):

    def start(self, *args, **kwargs):
        pass


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


class MockNodeClient(Mock):

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def shutdown(self):
        pass

    def take_snapshot(self):
        return defer.succeed(
            {'message': {'some': 'data'}, 'success': True}
        )


class TestBrokerServer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.patchs = [
            patch('pinky.broker.server.LoopingCall', MockLoopingCall),
            patch.object(BrokerServer, '__bases__', (MockBaseServer, ))
        ]
        super(TestBrokerServer, self).__init__(*args, **kwargs)

    def setUp(self):
        [p.start() for p in self.patchs]

    def tearDown(self):
        try:
            [p.stop() for p in self.patchs]
        except:
            pass

    def test_create(self):
        allowed_methods = (
            'register_node', 'set', 'get', 'mget',
            'delete', 'keys', 'sync_nodes'
        )
        server = BrokerServer.create(ADDRESS)
        self.assertEqual(server.__allowed_methods__, allowed_methods)
        self.assertEqual(server.__serializer__, MockJSONSerializer)
        self.assertIsInstance(server.factory, ZmqFactory)
        self.assertIsInstance(server.endpoints[0], ZmqEndpoint)
        self.assertEqual(server._node_client, NodeClient)
        self.assertEqual(server._hash_class, ConsistentHash)
        self.assertEqual(server._ping_timeout, 1)
        self.assertEqual(server._ping_frequencey, 5)
        self.assertEqual(server.num_nodes, 0)
        server.shutdown()

    def test_register_node(self):

        def verify_result(result):
            self.assertIsInstance(result, Success)
            self.assertTrue(result.success)
            self.assertEqual(result.message, None)

        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        d = broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )
        d.addCallback(verify_result)
        d.addCallback(lambda _: self.assertEqual(broker.num_nodes, 1))
        d.addCallback(lambda _: self.assertIsInstance(
            broker._connections['some_id'], MockNodeClient
        ))
        return d

    def test_register_node_wait_for_sync(self):

        def verify_result(result):
            self.assertIsInstance(result, Success)
            self.assertTrue(result.success)
            self.assertEqual(result.message, None)

        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.sync_nodes = Mock(
            side_affect=lambda: defer.succeed(None),
            return_value=defer.succeed(None)
        )
        d = broker.register_node(
            'some_id', 'some_address', wait_for_sync=True
        )
        d.addCallback(verify_result)
        d.addCallback(lambda _: self.assertEqual(broker.num_nodes, 1))
        d.addCallback(lambda _: self.assertIsInstance(
            broker._connections['some_id'], MockNodeClient
        ))
        return d

    def test_register_node_over_one(self):

        def verify_result(result):
            self.assertIsInstance(result, Success)
            self.assertTrue(result.success)
            self.assertEqual(result.message, None)

        dlist = []
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.sync_nodes = Mock(side_affect=lambda: defer.succeed(None))

        d1 = broker.register_node(
            'some_id1', 'some_address1', wait_for_sync=False
        )
        d1.addCallback(verify_result)
        d1.addCallback(lambda _: self.assertEqual(broker.num_nodes, 1))
        d1.addCallback(lambda _: self.assertEqual(len(broker._connections), 1))
        d1.addCallback(lambda _: self.assertFalse(broker.sync_nodes.called))
        dlist.append(d1)

        d2 = broker.register_node(
            'some_id2', 'some_address2', wait_for_sync=False
        )
        d2.addCallback(verify_result)
        d2.addCallback(lambda _: self.assertEqual(broker.num_nodes, 2))
        d2.addCallback(lambda _: self.assertEqual(len(broker._connections), 2))
        d2.addCallback(lambda _: self.assertTrue(broker.sync_nodes.called))
        dlist.append(d2)

        d3 = broker.register_node(
            'some_id3', 'some_address3', wait_for_sync=False
        )
        d3.addCallback(verify_result)
        d3.addCallback(lambda _: self.assertEqual(broker.num_nodes, 3))
        d3.addCallback(lambda _: self.assertEqual(len(broker._connections), 3))
        d3.addCallback(lambda _: self.assertTrue(broker.sync_nodes.called))
        dlist.append(d3)

        d = defer.DeferredList(dlist)
        return d

    def test_register_node_over_one_wait_for_sync(self):

        def verify_result(result):
            self.assertIsInstance(result, Success)
            self.assertTrue(result.success)
            self.assertEqual(result.message, None)

        dlist = []
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.sync_nodes = Mock(
            side_affect=lambda: defer.succeed(None),
            return_value=defer.succeed(None)
        )

        d1 = broker.register_node(
            'some_id1', 'some_address1', wait_for_sync=True
        )
        d1.addCallback(verify_result)
        d1.addCallback(lambda _: self.assertEqual(broker.num_nodes, 1))
        d1.addCallback(lambda _: self.assertEqual(len(broker._connections), 1))
        d1.addCallback(lambda _: self.assertFalse(broker.sync_nodes.called))
        dlist.append(d1)

        d2 = broker.register_node(
            'some_id2', 'some_address2', wait_for_sync=True
        )
        d2.addCallback(verify_result)
        d2.addCallback(lambda _: self.assertEqual(broker.num_nodes, 2))
        d2.addCallback(lambda _: self.assertEqual(len(broker._connections), 2))
        d2.addCallback(lambda _: self.assertTrue(broker.sync_nodes.called))
        dlist.append(d2)

        d3 = broker.register_node(
            'some_id3', 'some_address3', wait_for_sync=True
        )
        d3.addCallback(verify_result)
        d3.addCallback(lambda _: self.assertEqual(broker.num_nodes, 3))
        d3.addCallback(lambda _: self.assertEqual(len(broker._connections), 3))
        d3.addCallback(lambda _: self.assertTrue(broker.sync_nodes.called))
        dlist.append(d3)

        d = defer.DeferredList(dlist)
        return d

    def test_unregister_node(self):

        def verify_result(result):
            self.assertIsInstance(result, Success)
            self.assertTrue(result.success)
            self.assertEqual(result.message, None)

        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        d = broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )
        d.addCallback(verify_result)
        d.addCallback(lambda _: self.assertEqual(broker.num_nodes, 1))
        d.addCallback(lambda _: self.assertIsInstance(
            broker._connections['some_id'], MockNodeClient
        ))

        d.addCallback(lambda _: broker.unregister_node('some_id'))
        d.addCallback(lambda _: self.assertEqual(broker.num_nodes, 0))
        d.addCallback(lambda _: self.assertEqual(broker._connections, {}))
        return d

    def test_unregister_node_zero_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        self.assertRaises(ZeroNodes, broker.unregister_node, 'some_id')

    def test_get_node_by_key(self):

        def verify_result(result):
            self.assertIsInstance(result, Success)
            self.assertTrue(result.success)
            self.assertEqual(result.message, None)

        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        d = broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )
        d.addCallback(verify_result)
        d.addCallback(lambda _: self.assertEqual(broker.num_nodes, 1))
        d.addCallback(lambda _: self.assertIsInstance(
            broker._connections['some_id'], MockNodeClient
        ))

        d.addCallback(lambda _: broker.get_node_by_key('some_key'))
        d.addCallback(self.assertIsInstance, MockNodeClient)

        return d

    def test__take_snapshots(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.sync_nodes = Mock(side_affect=lambda: defer.succeed(None))
        broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )

        d = broker._take_snapshots()
        d.addCallback(self.assertEqual, {'some': 'data'})
        return d

    def test__sync_nodes(self):
        MockNodeClient.sync = Mock(
            side_affect=lambda: defer.succeed(None),
            return_value=defer.succeed(None)
        )
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )

        d = broker._sync_nodes({'key1': 'value1', 'key2': 'value2'})
        d.addCallback(lambda _: self.assertTrue(MockNodeClient.sync.called))
        return d

    def test_sync_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )

        d = broker.sync_nodes()
        d.addCallback(lambda suc: self.assertIsInstance(suc, Success))
        return d

    def test_sync_zero_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        self.assertRaises(ZeroNodes, broker.sync_nodes)
