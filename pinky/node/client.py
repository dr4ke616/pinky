from pinky.core.base import BaseClient


class NodeClient(BaseClient):

    def ping(self, timeout):
        return self.send_message('ping', timeout=timeout)
