from zope.interface import implementer
from pinky.core.interfaces import IStorage

from pinky.core.base import BaseClient


@implementer(IStorage)
class BrokerClient(BaseClient):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self.timeout = kwargs.pop('timeout', 1)

        super(BrokerClient, self).__init__(factory, endpoint, *args, **kwargs)

    def register_node(self, node_id, address, wait_for_sync=False):
        return self.send_message(
            'register_node', node_id, address, wait_for_sync
        )

    def sync_nodes(self):
        return self.send_message('sync_nodes')

    def _extract_data(self, response):
        if response['success'] is False:
            raise Exception(response['message'])

        return response['message']

    def set(self, key, value):
        d = super(BrokerClient, self).set(key, value, timeout=self.timeout)
        d.addCallback(self._extract_data)
        return d

    def get(self, key):
        d = super(BrokerClient, self).get(key, timeout=self.timeout)
        d.addCallback(self._extract_data)
        return d

    def mget(self, keys):
        d = super(BrokerClient, self).mget(keys, timeout=self.timeout)
        d.addCallback(self._extract_data)
        return d

    def delete(self, key):
        d = super(BrokerClient, self).delete(key, timeout=self.timeout)
        d.addCallback(self._extract_data)
        return d

    def keys(self, pattern):
        d = super(BrokerClient, self).keys(pattern, timeout=self.timeout)
        d.addCallback(self._extract_data)
        return d
