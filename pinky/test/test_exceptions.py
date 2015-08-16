from twisted.trial import unittest

from pinky.core.exceptions import PinkyException, ZeroNodes, NodeRegisterFailed


class TestExceptions(unittest.TestCase):

    def test_pinky_exception(self):
        try:
            raise PinkyException
        except PinkyException as err:
            self.assertEqual(err.code, 'PINKY_EXCEPTION')

    def test_zero_nodes_exception(self):
        try:
            raise ZeroNodes
        except PinkyException as err:
            self.assertEqual(err.code, 'ZERO_NODES')

    def test_node_register_fail_exception(self):
        try:
            raise NodeRegisterFailed
        except PinkyException as err:
            self.assertEqual(err.code, 'NODE_REGISTER_FAILED')
