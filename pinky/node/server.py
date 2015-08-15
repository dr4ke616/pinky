import uuid

from twisted.python import log
from zope.interface import implementer

from pinky.core.base import BaseServer
from pinky.core.response import Success
from pinky.core.interfaces import IStorage
from pinky.core.cache import InMemoryCache
from pinky.core.exceptions import NodeRegisterFailed


@implementer(IStorage)
class NodeServer(BaseServer):

    __allowed_methods__ = (
        'ping', 'set', 'get', 'mget', 'delete', 'keys', 'sync', 'take_snapshot'
    )

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
        if self._debug:
            log.msg('Storage contents >>> {} <<<'.format(self._cache_class))

        return Success('PONG')

    def sync(self, data):
        """ Update internal storage
        """
        self._cache_class.update(data)

    def take_snapshot(self):
        """ Take snapshot of the node's data
        """
        return Success(self._cache_class)

    def set(self, key, value):
        resp = self._cache_class.set(key, value)
        return Success(resp)

    def get(self, key):
        resp = self._cache_class.get(key)
        return Success(resp)

    def mget(self, keys):
        resp = self._cache_class.mget(keys)
        return Success(resp)

    def delete(self, key):
        resp = self._cache_class.delete(key)
        return Success(resp)

    def keys(self, pattern):
        resp = self._cache_class.keys(pattern)
        return Success(resp)
