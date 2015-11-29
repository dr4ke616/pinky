# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: service
    :platform: Unix, Windows
    :synopsis: Broker service
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from twisted.application import service

from pinky.core.manhole import ManholeServer
from pinky.broker.server import BrokerServer


class BrokerService(service.Service):
    """ Service to being started by twistd
        This service handles the broker server
    """

    def __init__(self, port, server=BrokerServer, **kwargs):
        self.name = 'BrokerService'
        self._debug = kwargs.get('debug', False)

        self.port = port
        self.server_class = server

        self.server = None
        self.manhole = None

        self._init_manhole(
            kwargs['ssh_user'], kwargs['ssh_password'],
            kwargs['ssh_port'], kwargs['activate_ssh_server']
        )

    def _init_manhole(self, user, password, port, activate=False):
        if not activate:
            return

        self.manhole = ManholeServer(user, password, port)
        self.manhole.setName('Pinky-Broker-SSH-Manhole-Service')

    def start(self):
        uri = 'tcp://0.0.0.0:{port}'.format(port=self.port)
        self.server = self.server_class.create(uri, debug=self._debug)

        if self.manhole:
            self.manhole.startService()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server = None

        if self.manhole:
            self.manhole.stopService()

    def startService(self):
        service.Service.startService(self)
        self.start()

    def stopService(self):
        service.Service.stopService(self)
        self.stop()
