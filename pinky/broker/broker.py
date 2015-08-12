import sys

from twisted.python import log
from twisted.internet import reactor

from lib.base_server import BaseServer


class BrokerServer(BaseServer):
    pass


def run_broker():
    log.startLogging(sys.stdout)

    BrokerServer.create('ipc:///tmp/broker.sock')

    reactor.run()
