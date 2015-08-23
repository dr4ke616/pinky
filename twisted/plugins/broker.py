from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from pinky.broker.service import BrokerService


class Options(usage.Options):
    optParameters = [
        ['port', 'p', 43435, 'The port number to listen on.'],
        ['host', 'h', '0.0.0.0', 'The host to run on.']
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
            host=options['host'],
            debug=options['debug']
        )


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = BrokerServiceMaker()
