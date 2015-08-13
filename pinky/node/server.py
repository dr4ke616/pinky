import uuid

from pinky.cache import InMemoryCache
from pinky.lib.base import BaseServer
from pinky.lib.serializer.msgpack_serializer import MSGPackSerializer


class NodeServer(BaseServer):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._id = None
        self._is_registered = False
        self._debug = kwargs.pop('debug', False)
        self._serializer = kwargs.pop('serializer', MSGPackSerializer)
        self._cache_class = kwargs.pop('cache', InMemoryCache)()

        super(NodeServer, self).__init__(factory, endpoint, *args, **kwargs)

    @property
    def id(self):
        if self._id is None:
            self._id = uuid.uuid4()

        return self._id

    def gotMessage(self, message_id, message):
        super(NodeServer, self).gotMessage(message_id, message)
        self.reply(message_id, 'some reply')

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
