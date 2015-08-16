import json
from mock import Mock, patch

from zope.interface import verify
from twisted.trial import unittest
from twisted.internet import defer
from zope.interface import implementer
from txzmq import ZmqEndpoint, ZmqFactory

from pinky.core.exceptions import ZeroNodes
from pinky.core.interfaces import ISerializer
from pinky.core.base import BaseClient, BaseServer
from pinky.core.response import (
    Response, Forbidden, InternalServerError, Fail, Success
)

ADDRESS = 'tcp://127.0.0.1:42000'


@implementer(ISerializer)
class MockJSONSerializer(object):
    """ Mock JSON serializer. Just used to json encode and decode
        for various test cases
    """

    @classmethod
    def dump(cls, content):
        if content is not None:
            return json.dumps(content)

    @classmethod
    def load(cls, content):
        if content is not None:
            return json.loads(content)


class MockLog(object):

    @classmethod
    def err(*args, **kwargs):
        pass

    @classmethod
    def msg(*args, **kwargs):
        pass


class MockZmq(object):

    def __init__(self, factory, endpoint, *args, **kwargs):
        self.factory = factory
        self.endpoints = [endpoint]

    def shutdown(self):
        pass


class MockBaseServer(MockZmq, BaseServer):

    __serializer__ = MockJSONSerializer
    __allowed_methods__ = (
        'test_remote', 'test_general_exception',
        'test_pinky_exception', 'test_success'
    )
    _debug = False

    def test_remote(self, my_arg):
        return 'You have been called {}'.format(my_arg)

    def test_success(self, my_arg):
        return Success(my_arg)

    def reply(self, message_id, resp):
        return resp

    def test_general_exception(self):
        raise Exception('Some Exception has been raised')

    def test_pinky_exception(self):
        raise ZeroNodes


class MockBaseClient(MockZmq, BaseClient):

    __serializer__ = MockJSONSerializer
    _debug = False

    def sendMsg(self, *args, **kwargs):
        pass


class TestBaseServerImplementer(unittest.TestCase):

    def test_interface(self):
        self.assertTrue(verify.verifyClass(ISerializer, MockJSONSerializer))


class TestBaseServer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBaseServer, self).__init__(*args, **kwargs)
        self.patch = patch('pinky.core.base.log', MockLog)

    def setUp(self):
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_create(self):
        server = MockBaseServer.create(ADDRESS)
        self.assertEqual(
            server.__allowed_methods__, MockBaseServer.__allowed_methods__
        )
        self.assertEqual(server.__serializer__, MockJSONSerializer)
        self.assertIsInstance(server.factory, ZmqFactory)
        self.assertIsInstance(server.endpoints[0], ZmqEndpoint)
        server.shutdown()

    def _create_server(self, serializer=MockJSONSerializer):
        factory = ZmqFactory()
        endpoint = ZmqEndpoint('bind', ADDRESS)
        server = MockBaseServer(factory, endpoint, serializer=serializer)
        self.assertEqual(
            server.__allowed_methods__, MockBaseServer.__allowed_methods__
        )
        self.assertEqual(server.__serializer__, MockJSONSerializer)
        self.assertIsInstance(server.factory, ZmqFactory)
        self.assertIsInstance(server.endpoints[0], ZmqEndpoint)
        return server

    def test_generate_response(self):
        server = self._create_server()
        response = server.generate_response(Response("some_data", True))
        self.assertEqual(response, '{"message": "some_data", "success": true}')
        server.shutdown()

    def test_generate_empty_response(self):
        server = self._create_server()
        response = server.generate_response(None)
        self.assertEqual(response, '{}')
        server.shutdown()

    def test_handle_message_args(self):
        raw_message = (
            '{"args": ["my_value"],'
            '"method": "test_remote",'
            '"kwargs": {}}'
        )
        server = self._create_server()
        response = server._handle_message(raw_message)
        self.assertEqual('You have been called my_value', response)

    def test_handle_message_kwargs(self):
        raw_message = (
            '{"args": [],'
            '"method": "test_remote",'
            '"kwargs": {"my_arg": "my_value"}}'
        )
        server = self._create_server()
        response = server._handle_message(raw_message)
        self.assertEqual('You have been called my_value', response)

    def test_handle_message_forbidden(self):
        raw_message = (
            '{"args": [],'
            '"method": "forbidden_method",'
            '"kwargs": {}}'
        )
        server = self._create_server()
        response = server._handle_message(raw_message)
        self.assertIsInstance(response, Forbidden)
        self.assertFalse(response.success)
        self.assertEqual(response.message, 'FORBIDDEN')

    def test_handle_message_exception(self):
        raw_message = (
            '{"args": [],'
            '"method": "test_general_exception",'
            '"kwargs": {}}'
        )
        server = self._create_server()
        response = server._handle_message(raw_message)
        self.assertIsInstance(response, InternalServerError)
        self.assertFalse(response.success)
        self.assertEqual(response.message, 'INTERNAL_SERVER_ERROR')

    def test_handle_message_pinky_exception(self):
        raw_message = (
            '{"args": [],'
            '"method": "test_pinky_exception",'
            '"kwargs": {}}'
        )
        server = self._create_server()
        response = server._handle_message(raw_message)
        self.assertIsInstance(response, Fail)
        self.assertFalse(response.success)
        self.assertEqual(response.message, 'ZERO_NODES')

    def test_got_message_args(self):
        raw_message = (
            '{"args": ["my_value"],'
            '"method": "test_success",'
            '"kwargs": {}}'
        )
        server = self._create_server()
        d = server.gotMessage(None, raw_message)
        d.addCallback(lambda resp: self.assertEqual(
            resp, '{"message": "my_value", "success": true}')
        )
        return d

    def test_got_message_kwargs(self):
        raw_message = (
            '{"args": [],'
            '"method": "test_success",'
            '"kwargs": {"my_arg": "my_value"}}'
        )
        server = self._create_server()
        d = server.gotMessage(None, raw_message)
        d.addCallback(lambda resp: self.assertEqual(
            resp, '{"message": "my_value", "success": true}')
        )
        return d


class TestBaseClient(unittest.TestCase):

    def test_create(self):
        server = MockBaseClient.create(ADDRESS)
        self.assertEqual(server.__serializer__, MockJSONSerializer)
        self.assertIsInstance(server.factory, ZmqFactory)
        self.assertIsInstance(server.endpoints[0], ZmqEndpoint)
        server.shutdown()

    def _create_client(self, serializer=MockJSONSerializer):
        factory = ZmqFactory()
        endpoint = ZmqEndpoint('connect', ADDRESS)
        server = MockBaseClient(factory, endpoint, serializer=serializer)
        self.assertEqual(server.__serializer__, MockJSONSerializer)
        self.assertIsInstance(server.factory, ZmqFactory)
        self.assertIsInstance(server.endpoints[0], ZmqEndpoint)
        return server

    def test_send_message_args(self):
        raw_response = (
            '{"success": true, "message": "some response"}'
        )
        MockBaseClient.sendMsg = Mock(
            side_effect=lambda *a, **kw: defer.succeed([raw_response])
        )
        client = self._create_client()
        d = client.send_message('some_method', 'some_arg')
        client.sendMsg.assert_called_once_with(
            '{"args": ["some_arg"], "method": "some_method", "kwargs": {}}',
            timeout=None
        )
        d.addCallback(lambda resp: self.assertEqual(
            resp, {"success": True, "message": "some response"})
        )
        return d

    def test_send_message_kwargs(self):
        raw_response = (
            '{"success": true, "message": "some response"}'
        )
        MockBaseClient.sendMsg = Mock(
            side_effect=lambda *a, **kw: defer.succeed([raw_response])
        )
        client = self._create_client()
        d = client.send_message('some_method', some_key='some_arg')
        client.sendMsg.assert_called_once_with(
            '{"args": [], "method": "some_method", "kwargs": {"some_key": "some_arg"}}',  # noqa
            timeout=None
        )
        d.addCallback(lambda resp: self.assertEqual(
            resp, {"success": True, "message": "some response"})
        )
        return d

    def test_send_message_decode_false(self):
        raw_response = (
            '{"success": true, "message": "some response"}'
        )
        MockBaseClient.sendMsg = Mock(
            side_effect=lambda *a, **kw: defer.succeed([raw_response])
        )
        client = self._create_client()
        d = client.send_message(
            'some_method', 'some_arg', decode_reponse=False
        )
        client.sendMsg.assert_called_once_with(
            '{"args": ["some_arg"], "method": "some_method", "kwargs": {}}',
            timeout=None
        )
        d.addCallback(lambda resp: self.assertEqual(
            resp, ['{"success": true, "message": "some response"}'])
        )
        return d

    def test_send_message_timeout(self):
        raw_response = (
            '{"success": true, "message": "some response"}'
        )
        MockBaseClient.sendMsg = Mock(
            side_effect=lambda *a, **kw: defer.succeed([raw_response])
        )
        client = self._create_client()
        d = client.send_message('some_method', 'some_arg', timeout=10)
        client.sendMsg.assert_called_once_with(
            '{"args": ["some_arg"], "method": "some_method", "kwargs": {}}',
            timeout=10
        )
        d.addCallback(lambda resp: self.assertEqual(
            resp, {"success": True, "message": "some response"})
        )
        return d

    def test_send_message_decode_false_timeout(self):
        raw_response = (
            '{"success": true, "message": "some response"}'
        )
        MockBaseClient.sendMsg = Mock(
            side_effect=lambda *a, **kw: defer.succeed([raw_response])
        )
        client = self._create_client()
        d = client.send_message(
            'some_method', 'some_arg', decode_reponse=False, timeout=15
        )
        client.sendMsg.assert_called_once_with(
            '{"args": ["some_arg"], "method": "some_method", "kwargs": {}}',
            timeout=15
        )
        d.addCallback(lambda resp: self.assertEqual(
            resp, ['{"success": true, "message": "some response"}'])
        )
        return d

    def test_set(self):
        response = {"success": True, "message": "some response"}
        client = self._create_client()
        client.send_message = Mock(
            side_effect=lambda *a, **kw: defer.succeed(response))

        d = client.set('some_key', 'some_value')
        client.send_message.assert_called_once_with(
            'set', 'some_key', 'some_value'
        )
        d.addCallback(self.assertEqual, response)
        return d

    def test_get(self):
        response = {"success": True, "message": "some response"}
        client = self._create_client()
        client.send_message = Mock(
            side_effect=lambda *a, **kw: defer.succeed(response))

        d = client.get('some_key')
        client.send_message.assert_called_once_with('get', 'some_key')
        d.addCallback(self.assertEqual, response)
        return d

    def test_mget(self):
        response = {"success": True, "message": "some response"}
        client = self._create_client()
        client.send_message = Mock(
            side_effect=lambda *a, **kw: defer.succeed(response))

        d = client.mget(['some_key1', 'some_key2', 'some_key3'])
        client.send_message.assert_called_once_with(
            'mget', ['some_key1', 'some_key2', 'some_key3']
        )
        d.addCallback(self.assertEqual, response)
        return d

    def test_delete(self):
        response = {"success": True, "message": "some response"}
        client = self._create_client()
        client.send_message = Mock(
            side_effect=lambda *a, **kw: defer.succeed(response))

        d = client.delete('some_key')
        client.send_message.assert_called_once_with('delete', 'some_key')
        d.addCallback(self.assertEqual, response)
        return d

    def test_keys(self):
        response = {"success": True, "message": "some response"}
        client = self._create_client()
        client.send_message = Mock(
            side_effect=lambda *a, **kw: defer.succeed(response))

        d = client.keys('some_key*')
        client.send_message.assert_called_once_with('keys', 'some_key*')
        d.addCallback(self.assertEqual, response)
        return d
