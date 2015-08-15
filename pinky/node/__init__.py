import sys

from twisted.python import log
from twisted.internet import reactor

from pinky.node.server import NodeServer
from pinky.node.client import NodeClient
from pinky.broker.client import BrokerClient


def run_server():
    log.startLogging(sys.stdout)

    server = NodeServer.create('tcp://127.0.0.1:43465', debug=True)
    server.register_with_broker(BrokerClient, 'tcp://127.0.0.1:43435')

    reactor.run()


def run_client():
    log.startLogging(sys.stdout)

    def doPrint(reply):
        print("Got reply: %s" % (reply))

    def onErr(reply):
        print("Got reply: %s" % (reply))

    client = NodeClient.create('tcp://127.0.0.1:43435', debug=True)

    d = client.sendMsg('Some message')
    d.addCallback(doPrint)
    d.addErrback(onErr)

    reactor.run()


__all__ = ['NodeServer', 'NodeClient']
