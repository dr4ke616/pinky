from twisted.trial import unittest

ADDRESS = 'tcp://127.0.0.1:42000'


class TestNodeServer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.patchs = []
        super(TestNodeServer, self).__init__(*args, **kwargs)

    def setUp(self):
        [p.start() for p in self.patchs]

    def tearDown(self):
        try:
            [p.stop() for p in self.patchs]
        except:
            pass

    def test_create(self):
        pass
