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
    client.set('some_key111', 'some_value')
    client.set('some_key222', 'some_value')
    client.set('some_key333', 'some_value')
    client.set('some_key444', 'some_value')

    d = client.get('some_key111')
    d.addCallback(doPrint)

    # d = client.mget(['some_key222'])
    # d.addCallback(doPrint)

    # d = client.keys('some_key*')
    # d.addCallback(doPrint)

    # d = client.delete('some_key222')
    # d.addCallback(doPrint)

    d.addCallback(lambda _: reactor.stop())

    reactor.run()


__all__ = ['BrokerServer', 'BrokerClient']
