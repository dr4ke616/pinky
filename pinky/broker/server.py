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


@implementer(IStorage)
class BrokerServer(BaseServer):

    __allowed_methods__ = (
        'register_node', 'set', 'get', 'mget', 'delete', 'keys'
    )

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._nodes = []
        self._connections = {}
        self._node_client = kwargs.pop('node_client', NodeClient)
        self._hash_class = kwargs.pop('hash_class', ConsistentHash)

        self._ping_timeout = kwargs.pop('ping_timeout', 1)
        self._ping_frequencey = kwargs.pop('ping_frequencey', 5)

        super(BrokerServer, self).__init__(factory, endpoint, *args, **kwargs)

        LoopingCall(self.ping_nodes).start(self._ping_frequencey)

    def register_node(self, node_id, address):
        log.msg(
            'Registering node {} with address of {}'.format(node_id, address)
        )
        self._nodes.append(node_id)

        client = self._node_client.create(address)
        self._connections[node_id] = client

        return Success('Register successful')

    def unregister_node(self, node_id):
        log.msg('Unregistering node {}'.format(node_id))

        node = self._connections[node_id]
        node.shutdown()
        del self._connections[node_id]

        self._nodes.remove(node_id)

    def ping_nodes(self):
        if self._debug:
            log.msg('Pinging nodes')

        def _on_failed_ping(err, node_id):
            if err.type == ZmqRequestTimeoutError:
                self.unregister_node(node_id)
                return

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
        ch = self._hash_class(len(self._nodes))
        machine = ch.get_machine(key)

        node_id = self._nodes[machine]
        return self._connections[node_id]

    def get(self, key):
        node = self.get_node_by_key(key)

        d = node.get(key)
        d.addCallback(lambda resp: Success(resp['message']))
        return d

    def mget(self, keys):
        # TODO: This may need to be corrected
        node = self.get_node_by_key(keys[0])

        d = node.mget(keys)
        d.addCallback(lambda resp: Success(resp['message']))
        return d

    def keys(self, pattern):
        # TODO: This may need to be corrected
        node = self.get_node_by_key(pattern)

        d = node.keys(pattern)
        d.addCallback(lambda resp: Success(resp['message']))
        return d

    def set(self, key, value, wait_for_all=True):
        node = self.get_node_by_key(key)
        dlist = [node.set(key, value)]

        if wait_for_all:
            for other_node in self._connections.values():
                if other_node == node:
                    continue

                dlist.append(other_node.set(key, value))

        d = defer.gatherResults(dlist)
        d.addCallback(lambda _: Success(None))
        return d

    def delete(self, key, wait_for_all=True):
        node = self.get_node_by_key(key)
        dlist = [node.delete(key)]

        if wait_for_all:
            for other_node in self._connections.values():
                if other_node == node:
                    continue

                dlist.append(other_node.delete(key))

        d = defer.gatherResults(dlist)
        d.addCallback(lambda _: Success(None))
        return d
