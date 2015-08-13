import sys

from twisted.python import log
from twisted.internet import reactor

from lib.base import BaseServer, BaseClient


class BrokerServer(BaseServer):
    pass


class BrokerClient(BaseClient):
    pass


def run_broker():
    log.startLogging(sys.stdout)

    BrokerServer.create('tcp://127.0.0.1:43435', debug=True)

    reactor.run()


def run_broker_client():

    def doPrint(reply):
        print("Got reply: %s" % (reply))

    def onErr(reply):
        print("Got reply: %s" % (reply))

    log.startLogging(sys.stdout)

    client = BrokerClient.create('tcp://127.0.0.1:43435', debug=True)
    d = client.sendMsg('Some message')
    d.addCallback(doPrint)
    d.addErrback(onErr)

    reactor.run()
