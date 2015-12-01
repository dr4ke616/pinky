from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from pinky.node.service import NodeService


class Options(usage.Options):
    optParameters = [
        ['port', None, None, 'The port number to listen on.'],
        ['host', None, None, 'The host address to bind to.'],
        ['broker_host', 'h', None, 'The broker host to connect to.'],
        ['broker_port', 'p', 43435, 'The broker port to connect to.']
    ]

    optFlags = [
        ['debug', 'b', 'Enable/disable debug mode.']
    ]


class NodeServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "node"
    description = "Startup an instance of the Pinky node"
    options = Options

    def makeService(self, options):
        """ Construct a Node Server
        """
        return NodeService(
            port=options['port'],
            host=options['host'],
            broker_host=options['broker_host'],
            broker_port=options['broker_port'],
            debug=options['debug']
        )


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = NodeServiceMaker()
