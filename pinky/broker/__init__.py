import sys

from twisted.python import log
from twisted.internet import reactor

from server import BrokerServer
from client import BrokerClient


def run_server():
    log.startLogging(sys.stdout)

    BrokerServer.create('tcp://127.0.0.1:43435', debug=True)

    reactor.run()


def run_client():
    log.startLogging(sys.stdout)

    def doPrint(reply):
        print("Got reply: %s" % (reply))

    def onErr(reply):
        print("Got reply: %s" % (reply))

    client = BrokerClient.create('tcp://127.0.0.1:43435', debug=True)
    client.register_node('some_id', 'tcp://127.0.0.1:43455')

    reactor.run()


__all__ = ['BrokerServer', 'BrokerClient']
