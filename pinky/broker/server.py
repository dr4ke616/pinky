import functools

from twisted.python import log
from twisted.internet import defer
from twisted.internet.task import LoopingCall

from zope.interface import implementer
from txzmq.req_rep import ZmqRequestTimeoutError

from pinky.core.base import BaseServer
from pinky.core.response import Success
from pinky.node.client import NodeClient
from pinky.core.interfaces import IStorage
from pinky.core.hash import ConsistentHash
from pinky.core.exceptions import ZeroNodes


def check_nodes(func):

    @functools.wraps(func)
    def decorator(self, *args, **kwargs):

        if self.num_nodes == 0:
            raise ZeroNodes

        return func(self, *args, **kwargs)

    return decorator


@implementer(IStorage)
class BrokerServer(BaseServer):

    __allowed_methods__ = (
        'register_node', 'set', 'get', 'mget', 'delete', 'keys', 'sync_nodes'
    )

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._connections = {}
        self._node_client = kwargs.pop('node_client', NodeClient)
        self._hash_class = kwargs.pop('hash_class', ConsistentHash)

        self._ping_timeout = kwargs.pop('ping_timeout', 1)
        self._ping_frequencey = kwargs.pop('ping_frequencey', 5)

        super(BrokerServer, self).__init__(factory, endpoint, *args, **kwargs)

        LoopingCall(self.ping_nodes).start(self._ping_frequencey)

    @property
    def num_nodes(self):
        return len(self._connections)

    @property
    def nodes(self):
        return self._connections.values()

    @property
    def node_ids(self):
        return self._connections.keys()

    def register_node(self, node_id, address, wait_for_sync):
        log.msg(
            'Registering node {} with address of {}'.format(node_id, address)
        )
        client = self._node_client.create(address)
        self._connections[node_id] = client

        if self.num_nodes > 1:
            d = self.sync_nodes()
            if wait_for_sync:
                d.addCallback(lambda _: Success(None))
                return d
            else:
                return defer.succeed(Success(None))
        else:
            return defer.succeed(Success(None))

    @check_nodes
    def unregister_node(self, node_id):
        log.msg('Unregistering node {}'.format(node_id))

        node = self._connections[node_id]
        node.shutdown()
        del self._connections[node_id]

    def _take_snapshots(self):
        """ Take snapshots of all nodes
        """
        data = {}
        d = defer.gatherResults([
            node.take_snapshot().addCallback(
                lambda res: data.update(res['message'])) for node in self.nodes
        ])
        d.addCallback(lambda _: data)
        return d

    def _sync_nodes(self, data):
        d = defer.gatherResults([node.sync(data) for node in self.nodes])
        return d

    @check_nodes
    def sync_nodes(self):

        # TODO: Error validation, what happens if we cant sync?
        d = self._take_snapshots()
        d.addCallback(self._sync_nodes)
        d.addCallback(lambda _: Success(None))
        return d

    def ping_nodes(self):
        if self._debug:
            log.msg('Pinging nodes')

        def _on_failed_ping(err, node_id):
            if err.type == ZmqRequestTimeoutError:
                try:
                    self.unregister_node(node_id)
                except ZeroNodes:
                    pass
            else:
                raise err  # re-raise the error

        for node_id, node in self._connections.items():
            d = node.ping(self._ping_timeout)
            if self._debug:
                d.addCallback(lambda msg, node_id: log.msg(
                    'Recieved message from node {}. {}'
                    ''.format(node_id, msg)), node_id
                )

            d.addErrback(_on_failed_ping, node_id)

    def get_node_by_key(self, key):
        """ Get a machine based off the key that the clinet
            sends up.
            :return: `pinky.node.clinet.NodeClient` instance
        """
        ch = self._hash_class(self.num_nodes)
        machine = ch.get_machine(key)

        node_id = self.node_ids[machine]
        return self._connections[node_id]

    def _distribute_to_nodes(self, operation, node, *args, **kwargs):
        wait_for_all = kwargs.pop('wait_for_all', True)
        dlist = [getattr(node, operation)(*args, **kwargs)]

        for other_node in self._connections.values():
            if other_node == node:
                continue

            d = getattr(other_node, operation)(*args, **kwargs)
            if wait_for_all:
                dlist.append(d)

        d = defer.gatherResults(dlist)
        # TODO: Check defer list for errors, see if we need to try again
        # Also - we're sending to many nodes, so if we fail on one after,
        # a certain amount of retries, do we roleback the other nodes ?
        d.addCallback(lambda _: Success(None))
        return d

    @check_nodes
    def get(self, key):
        node = self.get_node_by_key(key)

        d = node.get(key)
        d.addCallback(lambda resp: Success(resp['message']))
        return d

    @check_nodes
    def mget(self, keys):
        # TODO: This may need to be corrected
        node = self.get_node_by_key(keys[0])

        d = node.mget(keys)
        d.addCallback(lambda resp: Success(resp['message']))
        return d

    @check_nodes
    def keys(self, pattern):
        # TODO: This may need to be corrected
        node = self.get_node_by_key(pattern)

        d = node.keys(pattern)
        d.addCallback(lambda resp: Success(resp['message']))
        return d

    @check_nodes
    def set(self, key, value, wait_for_all=True):
        node = self.get_node_by_key(key)
        d = self._distribute_to_nodes(
            'set', node, key, value, wait_for_all=wait_for_all
        )
        return d

    @check_nodes
    def delete(self, key, wait_for_all=True):
        node = self.get_node_by_key(key)
        d = self._distribute_to_nodes(
            'delete', node, key, wait_for_all=wait_for_all
        )
        return d
