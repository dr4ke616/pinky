from pinky.core.base import BaseClient


class NodeClient(BaseClient):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self._debug = kwargs.pop('debug', False)

        super(NodeClient, self).__init__(factory, endpoint, *args, **kwargs)
