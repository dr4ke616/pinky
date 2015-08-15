from zope.interface import implementer

from pinky.core.base import BaseClient
from pinky.core.interfaces import IStorage


@implementer(IStorage)
class NodeClient(BaseClient):

    def ping(self, timeout):
        return self.send_message('ping', timeout=timeout)
