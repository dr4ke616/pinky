from twisted.python import log

from pinky.node import NodeClient
from pinky.lib.base import BaseServer
from pinky.lib.serializer.msgpack_serializer import MSGPackSerializer


class BrokerServer(BaseServer):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._nodes = []
        self._connections = {}
        self._debug = kwargs.pop('debug', False)
        self._node_client = kwargs.pop('node_client', NodeClient)
        self._serializer = kwargs.pop('serializer', MSGPackSerializer)

        self._allowed_methods = ('register_node', )
        super(BrokerServer, self).__init__(factory, endpoint, *args, **kwargs)

    def gotMessage(self, message_id, message):
        """ Message comes in the data structure as:
            {
                'method': 'some_method',
                'args': ['list', 'of', 'args'],
                'kwargs': {'key': 'value'}
            }
        """
        super(BrokerServer, self).gotMessage(message_id, message)
        resp = self._handle_message(message)
        self.reply(message_id, resp)

    def _handle_message(self, message):
        message = self._serializer.load(message)
        if self._debug:
            log.msg(message)

        method = message['method']
        args, kwargs = message['args'], message['kwargs']

        if method not in self._allowed_methods:
            return self.generate_fail_resp('FORBIDDEN')

        return getattr(self, method)(*args, **kwargs)

    def register_node(self, node_id, address):

        self._nodes.append(node_id)

        client = self._node_client.create(address)
        self._connections[node_id] = client

        return self.generate_success_resp('Register successful')
