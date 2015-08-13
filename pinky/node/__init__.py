import sys

from twisted.python import log
from twisted.internet import reactor

from server import NodeServer
from client import NodeClient

def run_server():
    log.startLogging(sys.stdout)

    NodeServer.create('tcp://127.0.0.1:43435', debug=True)

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



__all__ = ['NodeServer', 'run_node']
