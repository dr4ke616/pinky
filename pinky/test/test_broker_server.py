from mock import Mock, patch
from twisted.internet import defer

from pinky.core.response import Success
from pinky.node.client import NodeClient
from pinky.core.hash import ConsistentHash
from pinky.core.exceptions import ZeroNodes
from pinky.broker.server import BrokerServer

from helper import BaseTestServer, MockJSONSerializer, ZmqEndpoint, ZmqFactory

ADDRESS = 'tcp://127.0.0.1:42000'


class MockLoopingCall(Mock):

    def start(self, *args, **kwargs):
        pass


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


class TestBrokerServer(BaseTestServer):

    server = BrokerServer

    def __init__(self, *args, **kwargs):
        super(TestBrokerServer, self).__init__(*args, **kwargs)
        self.add_patch(
            patch('pinky.broker.server.LoopingCall', MockLoopingCall)
        )

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

    def test_ping_nodes(self):
        MockNodeClient.ping = Mock(
            side_affect=lambda: defer.succeed(None),
            return_value=defer.succeed(None)
        )
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )

        broker.ping_nodes()
        self.assertTrue(MockNodeClient.ping.called)

    def test__distribute_to_nodes(self):
        MockNodeClient.sync = Mock(
            side_affect=lambda: defer.succeed(None),
            return_value=defer.succeed(True)
        )
        MockNodeClient.set = Mock(
            side_affect=lambda: defer.succeed(None),
            return_value=defer.succeed(True)
        )
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker.register_node(
            'some_id1', 'some_address1', wait_for_sync=False
        )
        broker.register_node(
            'some_id2', 'some_address2', wait_for_sync=False
        )

        main_node = broker._connections['some_id1']
        d = broker._distribute_to_nodes('set', main_node)
        d.addCallback(
            lambda _: self.assertEqual(MockNodeClient.set.call_count, 2)
        )
        return d

    def _create_n_register_node_for_operations(self):
        """ Heavily verbos method for creating a broker ready to be tested
            against the persistent operations (as in set/get/mget/etc)
        """
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        broker._distribute_to_nodes = Mock(return_value=defer.succeed(None))
        broker.register_node(
            'some_id', 'some_address', wait_for_sync=False
        )
        return broker

    def test_set(self):
        node = MockNodeClient()
        broker = self._create_n_register_node_for_operations()
        broker.get_node_by_key = Mock(return_value=node)

        d = broker.set('some_key', 'some_value')
        d.addCallback(
            lambda _: broker.get_node_by_key.assert_called_with('some_key')
        )
        d.addCallback(lambda _: broker._distribute_to_nodes.assert_called_with(
            'set', node, 'some_key', 'some_value', wait_for_all=True
        ))
        return d

    def test_get(self):
        node = MockNodeClient()
        node.get = Mock(return_value=defer.succeed(
            {'message': None, 'success': True})
        )
        broker = self._create_n_register_node_for_operations()
        broker.get_node_by_key = Mock(return_value=node)

        d = broker.get('some_key')
        d.addCallback(
            lambda _: broker.get_node_by_key.assert_called_with('some_key')
        )
        d.addCallback(lambda _: node.get.assert_called_with('some_key'))
        return d

    def test_mget(self):
        node = MockNodeClient()
        node.get = Mock(return_value=defer.succeed(
            {'message': None, 'success': True})
        )
        broker = self._create_n_register_node_for_operations()
        broker.get_node_by_key = Mock(return_value=node)

        d = broker.mget(['some_key1', 'some_key2'])
        d.addCallback(
            lambda _: broker.get_node_by_key.assert_called_with('some_key1')
        )
        d.addCallback(
            lambda _: node.get.assert_called_with(['some_key1', 'some_key2'])
        )
        return d

    def test_delete(self):
        node = MockNodeClient()
        broker = self._create_n_register_node_for_operations()
        broker.get_node_by_key = Mock(return_value=node)

        d = broker.delete('some_key')
        d.addCallback(
            lambda _: broker.get_node_by_key.assert_called_with('some_key')
        )
        d.addCallback(lambda _: broker._distribute_to_nodes.assert_called_with(
            'delete', node, 'some_key', wait_for_all=True
        ))
        return d

    def test_keys(self):
        node = MockNodeClient()
        node.keys = Mock(return_value=defer.succeed(
            {'message': None, 'success': True})
        )
        broker = self._create_n_register_node_for_operations()
        broker.get_node_by_key = Mock(return_value=node)

        d = broker.keys('some_key*')
        d.addCallback(
            lambda _: broker.get_node_by_key.assert_called_with('some_key*')
        )
        d.addCallback(lambda _: node.keys.assert_called_with('some_key*'))
        return d

    def test_set_zero_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        self.assertRaises(ZeroNodes, broker.set, 'some_key', 'some_value')

    def test_get_zero_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        self.assertRaises(ZeroNodes, broker.set, 'some_key')

    def test_mget_zero_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        self.assertRaises(ZeroNodes, broker.set, ['some_key'])

    def test_keys_zero_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        self.assertRaises(ZeroNodes, broker.set, 'some_key*')

    def test_delete_zero_nodes(self):
        broker = BrokerServer.create(ADDRESS, node_client=MockNodeClient)
        self.assertRaises(ZeroNodes, broker.set, 'some_key')
