from twisted.python import log
from twisted.internet.task import LoopingCall

from zope.interface import implementer
from txzmq.req_rep import ZmqRequestTimeoutError

from pinky.node.client import NodeClient

from pinky.core.base import BaseServer
from pinky.core.interfaces import IStorage


@implementer(IStorage)
class BrokerServer(BaseServer):

    __allowed_methods__ = ('register_node', )

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._nodes = []
        self._connections = {}
        self._node_client = kwargs.pop('node_client', NodeClient)

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

        return self.generate_success_resp('Register successful')

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

    def set(self, key, value):
        pass

    def get(self, key):
        pass

    def mget(self, keys):
        pass

    def delete(self, key):
        pass

    def keys(self, pattern):
        pass

    def _fire_command(self, command):
        pass
