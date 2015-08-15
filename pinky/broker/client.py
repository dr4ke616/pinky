
from pinky.core.base import BaseClient


class BrokerClient(BaseClient):

    def register_node(self, node_id, address):
        return self.send_message(
            'register_node', node_id=node_id, address=address
        )
