from zope.interface import implementer
from pinky.core.interfaces import IStorage

from pinky.core.base import BaseClient


@implementer(IStorage)
class BrokerClient(BaseClient):

    def register_node(self, node_id, address):
        return self.send_message(
            'register_node', node_id=node_id, address=address
        )
