# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: service
    :platform: Unix, Windows
    :synopsis: Broker service
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from twisted.application import service

from pinky.broker.server import BrokerServer


class BrokerService(service.Service):
    """ Service to being started by twistd
        This service handles the broker server
    """

    def __init__(self, port, host='0.0.0.0', server=BrokerServer, **kwargs):
        self.name = 'BrokerService'
        self._debug = kwargs.get('debug', False)

        self.host = host
        self.port = port
        self.server_class = server

        self.server = None

    def start(self):
        uri = 'tcp://{host}:{port}'.format(host=self.host, port=self.port)
        self.server = self.server_class.create(uri, debug=self._debug)

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
