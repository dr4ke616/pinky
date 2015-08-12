from twisted.python import log

from txzmq import ZmqREPConnection, ZmqFactory, ZmqEndpoint


class BaseServer(ZmqREPConnection):

    def gotMessage(self, message_id, message):
        super(BaseServer, self).gotMessage(message_id, message)

    def reply(self, message_id, message):
        super(BaseServer, self).reply(message_id, message)

    @classmethod
    def create(cls, address, *args, **kwargs):
        log.msg('Creating {} on address {}'.format(cls.__name__, address))
        endpoint = ZmqEndpoint('bind', address)
        factory = ZmqFactory()
        return cls(factory, endpoint, *args, **kwargs)
