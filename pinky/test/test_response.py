from twisted.trial import unittest

from pinky.core.response import (
    Response, Success, InternalServerError, Forbidden, Fail
)


class TestResponse(unittest.TestCase):

    def test_response(self):
        r = Response('some_response', False)
        self.assertEqual(r.message, 'some_response')
        self.assertFalse(r.success)

    def test_success(self):
        r = Success('some other response')
        self.assertEqual(r.message, 'some other response')
        self.assertTrue(r.success)

    def test_internal_server_error(self):
        r = InternalServerError()
        self.assertEqual(r.message, 'INTERNAL_SERVER_ERROR')
        self.assertFalse(r.success)

    def test_forbidden(self):
        r = Forbidden()
        self.assertEqual(r.message, 'FORBIDDEN')
        self.assertFalse(r.success)

    def test_fail(self):
        r = Fail('some_failure')
        self.assertEqual(r.message, 'some_failure')
        self.assertFalse(r.success)
