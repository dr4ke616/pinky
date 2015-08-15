from twisted.python import log

from txzmq import ZmqREPConnection, ZmqFactory, ZmqEndpoint, ZmqREQConnection


class BaseServerMixin(object):

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


class BaseServer(ZmqREPConnection, BaseServerMixin):

    @classmethod
    def create(cls, address, *args, **kwargs):
        log.msg('Creating {} on address {}'.format(cls.__name__, address))
        return cls(
            ZmqFactory(), ZmqEndpoint('bind', address), *args, **kwargs
        )

    def gotMessage(self, message_id, message):
        if self._debug:
            log.msg('Server received message')


class BaseClient(ZmqREQConnection, BaseServerMixin):

    @classmethod
    def create(cls, address, *args, **kwargs):
        log.msg('Creating {} on address {}'.format(cls.__name__, address))
        return cls(
            ZmqFactory(), ZmqEndpoint('connect', address), *args, **kwargs
        )

    def gotMessage(self, message_id, message):
        if self._debug:
            log.msg('Client got message {}'.format(message))

    def sendMsg(self, message, *args, **kwargs):
        if self._debug:
            log.msg('Client sending message')

        return super(BaseClient, self).sendMsg(message, *args, **kwargs)
