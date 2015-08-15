from twisted.python import log
from twisted.internet import defer

from txzmq import ZmqREPConnection, ZmqFactory, ZmqEndpoint, ZmqREQConnection

from pinky.core.serializer.msgpack_serializer import MSGPackSerializer


class BaseServer(ZmqREPConnection):

    __allowed_methods__ = None

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._debug = kwargs.pop('debug', False)
        self._serializer = kwargs.pop('serializer', MSGPackSerializer)

        self._allowed_methods = ('ping', )
        super(BaseServer, self).__init__(factory, endpoint, *args, **kwargs)

    @classmethod
    def create(cls, address, *args, **kwargs):
        log.msg('Creating {} on address {}'.format(cls.__name__, address))
        return cls(
            ZmqFactory(), ZmqEndpoint('bind', address), *args, **kwargs
        )

    def gotMessage(self, message_id, message):
        """ Message comes in the data structure as:
            {
                'method': 'some_method',
                'args': ['list', 'of', 'args'],
                'kwargs': {'key': 'value'}
            }
        """
        d = defer.maybeDeferred(self._handle_message, message)
        d.addCallback(lambda resp: self.reply(message_id, resp))
        return d

    def _handle_message(self, message):
        message = self._serializer.load(message)
        if self._debug:
            log.msg('Server recieved message {}'.format(message))

        method = message['method']
        args, kwargs = message['args'], message['kwargs']

        if method not in self.__allowed_methods__:
            if self._debug:
                log.msg('Forbidden method call {}'.format(method))

            return self.generate_fail_resp('FORBIDDEN')

        try:
            return getattr(self, method)(*args, **kwargs)
        except Exception:
            log.err('Failed to execute {}'.format(method))
            log.err()  # log traceback
            return self.generate_fail_resp('INTERNAL_SERVER_ERROR')

    def generate_success_resp(self, message):
        return self._serializer.dump({
            'success': True,
            'message': message
        })

    def generate_fail_resp(self, message):
        return self._serializer.dump({
            'success': False,
            'message': message
        })


class BaseClient(ZmqREQConnection):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._debug = kwargs.pop('debug', False)
        self._serializer = kwargs.pop('serializer', MSGPackSerializer)

        super(BaseClient, self).__init__(factory, endpoint, *args, **kwargs)

    @classmethod
    def create(cls, address, *args, **kwargs):
        log.msg('Creating {} on address {}'.format(cls.__name__, address))
        return cls(
            ZmqFactory(), ZmqEndpoint('connect', address), *args, **kwargs
        )

    def gotMessage(self, message_id, message):
        if self._debug:
            log.msg('Client got message {}'.format(message))

    def connectionLost(self, reason):
        print('connection on {} closed'.format(self.__class__.__name__))
        print(reason)

    def send_message(self, method, *args, **kwargs):
        decode = kwargs.pop('decode_reponse', True)
        timeout = kwargs.pop('timeout', None)

        data = {'method': method, 'args': args, 'kwargs': kwargs}
        if self._debug:
            log.msg('Client sending message {}'.format(data))

        message = self._serializer.dump(data)
        d = self.sendMsg(message, timeout=timeout)
        if decode:
            d.addCallback(lambda r: self._serializer.load(r[0]))
        return d
