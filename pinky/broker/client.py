
from pinky.core.base import BaseClient
from pinky.core.serializer.msgpack_serializer import MSGPackSerializer


class BrokerClient(BaseClient):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._debug = kwargs.pop('debug', False)
        self._serializer = kwargs.pop('serializer', MSGPackSerializer)

        super(BrokerClient, self).__init__(factory, endpoint, *args, **kwargs)

    def _send(self, method, *args, **kwargs):
        data = {'method': method, 'args': args, 'kwargs': kwargs}
        message = self._serializer.dump(data)
        return self.sendMsg(message)

    def register_node(self, node_id, address):
        d = self._send('register_node', node_id=node_id, address=address)
        d.addCallback(lambda r: self._serializer.load(r[0]))
        return d
