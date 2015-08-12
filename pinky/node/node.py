import sys

from twisted.python import log
from twisted.internet import reactor

from lib.base_server import BaseServer


class NodeServer(BaseServer):
    pass


def run_node():
    log.startLogging(sys.stdout)

    NodeServer.create('ipc:///tmp/node.sock')

    reactor.run()
