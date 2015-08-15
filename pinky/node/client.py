from zope.interface import implementer

from pinky.core.base import BaseClient
from pinky.core.interfaces import IStorage


@implementer(IStorage)
class NodeClient(BaseClient):

    def ping(self, timeout):
        return self.send_message('ping', timeout=timeout)

    def sync(self, data):
        return self.send_message('sync', data)

    def take_snapshot(self):
        return self.send_message('take_snapshot')
