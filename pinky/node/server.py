import uuid

from twisted.python import log

from pinky.cache import InMemoryCache
from pinky.lib.base import BaseServer
from pinky.lib.exceptions import NodeRegisterFailed
from pinky.lib.serializer.msgpack_serializer import MSGPackSerializer


class NodeServer(BaseServer):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._id = None
        self._is_registered = False
        self._address = endpoint.address
        self._debug = kwargs.pop('debug', False)
        self._serializer = kwargs.pop('serializer', MSGPackSerializer)
        self._cache_class = kwargs.pop('cache', InMemoryCache)()

        super(NodeServer, self).__init__(factory, endpoint, *args, **kwargs)

    @property
    def id(self):
        if self._id is None:
            self._id = str(uuid.uuid4())

        return self._id

    def gotMessage(self, message_id, message):
        super(NodeServer, self).gotMessage(message_id, message)
        self.reply(message_id, 'some reply')

    def register_with_broker(self, broker, address):
        if self._is_registered is True:
            return

        def check_resp(resp):
            if resp['success'] is False:
                raise NodeRegisterFailed(resp['message'])

            log.msg('Successfully registered node {}'.format(self.id))
            self._is_registered = True

        d = broker.create(
            address, debug=self._debug).register_node(self.id, self._address)
        d.addCallback(check_resp)
        return d

    def set(self, key, value):
        return self._cache_class.set(key, value)

    def get(self, key):
        return self._cache_class.get(key)

    def mget(self, keys):
        return self._cache_class.mget(keys)

    def delete(self, key):
        return self._cache_class.delete(key)

    def keys(self, pattern):
        return self._cache_class.keys(pattern)
