import uuid

from twisted.python import log
from zope.interface import implementer

from pinky.core.base import BaseServer
from pinky.core.interfaces import IStorage
from pinky.core.cache import InMemoryCache
from pinky.core.exceptions import NodeRegisterFailed


@implementer(IStorage)
class NodeServer(BaseServer):

    __allowed_methods__ = ('ping', )

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._id = None
        self._is_registered = False
        self._address = endpoint.address
        self._cache_class = kwargs.pop('cache', InMemoryCache)()

        super(NodeServer, self).__init__(factory, endpoint, *args, **kwargs)

    @property
    def id(self):
        if self._id is None:
            self._id = str(uuid.uuid4())

        return self._id

    def register_with_broker(self, broker, address):
        if self._is_registered is True:
            return

        broker = broker.create(address, debug=self._debug)

        d = broker.register_node(self.id, self._address)
        d.addCallback(self._register)
        d.addCallback(lambda _: broker.shutdown())
        return d

    def _register(self, message):
        if message['success'] is False:
            raise NodeRegisterFailed(message['message'])

        log.msg(
            'I am successfully registered with ID {} on '
            'address {}'.format(self.id, self._address)
        )
        self._is_registered = True

    def ping(self):
        """ When we get a ping request from the broker,
            send back a PONG to tell it we are up
        """
        return self.generate_success_resp('PONG')

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
