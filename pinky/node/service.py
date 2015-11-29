# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: service
    :platform: Unix, Windows
    :synopsis: Node service
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from twisted.application import service

from pinky.node.server import NodeServer
from pinky.broker.client import BrokerClient


class NodeService(service.Service):
    """ Service to being started by twistd
        This service handles the node server
    """

    def __init__(self, port, server=NodeServer, **kwargs):
        self.name = 'NodeService'
        self._debug = kwargs.get('debug', False)

        self.broker_host = kwargs['broker_host']
        self.broker_port = kwargs.get('broker_port', 43435)

        self.port = port
        self.server_class = server

        self.server = None

    def start(self):
        uri = 'tcp://0.0.0.0:{port}'.format(port=self.port)
        self.server = self.server_class.create(uri, debug=self._debug)

        uri = 'tcp://{host}:{port}'.format(
            host=self.broker_host, port=self.broker_port
        )
        self.server.register_with_broker(BrokerClient, uri)

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server = None

    def startService(self):
        service.Service.startService(self)
        self.start()

    def stopService(self):
        service.Service.stopService(self)
        self.stop()
