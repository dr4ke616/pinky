from zope.interface import implementer
from pinky.core.interfaces import IStorage

from pinky.core.base import BaseClient


@implementer(IStorage)
class BrokerClient(BaseClient):

    def register_node(self, node_id, address, wait_for_sync=False):
        return self.send_message(
            'register_node', node_id, address, wait_for_sync
        )

    def sync_nodes(self):
        return self.send_message('sync_nodes')
