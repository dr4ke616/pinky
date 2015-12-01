from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from pinky.broker.service import BrokerService


class Options(usage.Options):
    optParameters = [
        ['port', None, 43435, 'The port number to listen on.'],
        ['activate-ssh-server', None, False,
            'Activate an SSH server on the broker for live debuging.'],
        ['ssh-user', None, None, 'SSH username.'],
        ['ssh-password', None, None, 'SSH pasword.'],
        ['ssh-port', None, None, 'SSH port to listen on.']
    ]

    optFlags = [
        ['debug', 'b', 'Enable/disable debug mode.']
    ]


class BrokerServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "broker"
    description = "Startup an instance of the Pinky broker"
    options = Options

    def makeService(self, options):
        """ Construct a Broker Server
        """
        return BrokerService(
            port=options['port'],
            debug=options['debug'],
            activate_ssh_server=options['activate-ssh-server'],
            ssh_user=options['ssh-user'],
            ssh_password=options['ssh-password'],
            ssh_port=options['ssh-port']
        )


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = BrokerServiceMaker()
