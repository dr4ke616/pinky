from twisted.python import log

from txzmq import ZmqREPConnection, ZmqFactory, ZmqEndpoint, ZmqREQConnection


class BaseServer(ZmqREPConnection):

    def gotMessage(self, message_id, message):
        if self._debug:
            log.msg('Server got message {}'.format(message))

    @classmethod
    def create(cls, address, *args, **kwargs):
        log.msg('Creating {} on address {}'.format(cls.__name__, address))
        debug = kwargs.pop('debug', False)

        client = cls(
            ZmqFactory(), ZmqEndpoint('bind', address), *args, **kwargs
        )
        client._debug = debug
        return client


class BaseClient(ZmqREQConnection):

    @classmethod
    def create(cls, address, *args, **kwargs):
        log.msg('Creating {} on address {}'.format(cls.__name__, address))
        debug = kwargs.pop('debug', False)

        client = cls(
            ZmqFactory(), ZmqEndpoint('connect', address), *args, **kwargs
        )
        client._debug = debug
        return client

    def sendMsg(self, message, *args, **kwargs):
        if self._debug:
            log.msg('Client sending message {}'.format(message))

        return super(BaseClient, self).sendMsg(message, *args, **kwargs)

    def gotMessage(self, message_id, message):
        if self._debug:
            log.msg('Client got message {}'.format(message))