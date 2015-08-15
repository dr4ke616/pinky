from twisted.python import log
from twisted.internet import defer

from txzmq import ZmqREPConnection, ZmqFactory, ZmqEndpoint, ZmqREQConnection

from pinky.core.response import InternalServerError, Forbidden
from pinky.core.serializer.msgpack_serializer import MSGPackSerializer


class BaseServer(ZmqREPConnection):

    __allowed_methods__ = None
    __serializer__ = MSGPackSerializer

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._debug = kwargs.pop('debug', False)

        serializer = kwargs.pop('serializer', None)
        if serializer:
            self.__serializer__ = serializer

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
        d.addCallback(self.generate_response)
        d.addCallback(lambda resp: self.reply(message_id, resp))
        return d

    def _handle_message(self, message):
        message = self.__serializer__.load(message)
        if self._debug:
            log.msg('Server recieved message {}'.format(message))

        method = message['method']
        args, kwargs = message['args'], message['kwargs']

        if method not in self.__allowed_methods__:
            if self._debug:
                log.msg('Forbidden method call {}'.format(method))

            return Forbidden()

        try:
            return getattr(self, method)(*args, **kwargs)
        except Exception:
            log.err('Failed to execute {}'.format(method))
            log.err()  # log traceback
            return InternalServerError()

    def generate_response(self, response):
        """ Serializes the response object and returns the
            raw form.
            :param response: A `pinky.core.response.Response`
                object
        """
        return self.__serializer__.dump(response.to_dict())


class BaseClient(ZmqREQConnection):

    __serializer__ = MSGPackSerializer

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._debug = kwargs.pop('debug', False)

        serializer = kwargs.pop('serializer', None)
        if serializer:
            self.__serializer__ = serializer

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

    def send_message(self, method, *args, **kwargs):
        decode = kwargs.pop('decode_reponse', True)
        timeout = kwargs.pop('timeout', None)

        data = {'method': method, 'args': args, 'kwargs': kwargs}
        if self._debug:
            log.msg('Client sending message {}'.format(data))

        message = self.__serializer__.dump(data)
        d = self.sendMsg(message, timeout=timeout)
        if decode:
            d.addCallback(lambda r: self.__serializer__.load(r[0]))
        return d
