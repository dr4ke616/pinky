# Copyright (c) 2015 Adam Drakeford <adam.drakeford@betbright.com>
# See LICENSE for more details

"""
.. module:: response
    :platform: Unix, Windows
    :synopsys: response module
.. moduleauthor:: Adam Drakeford <adam.drakeford@betbright.com>
"""
from zope.interface import implementer

from pinky.core.interfaces import IResponse


class Response(object):
    """ Response used to be returned to either node or broker
        client
        :param message: The message to be sent back, can be in
            the form of a string, list, or dict
        :param success: boolean indicating the success of the
            response
    """

    def __init__(self, message, success):
        self.message = message
        self.success = success

    def to_dict(self):
        """ Encode object to a dictionary
        """
        return {
            'success': self.success,
            'message': self.message
        }

    def __repr__(self):
        """ Rrepresent the object as a string
        """
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(map(repr, [self.message, self.success]))
        )


@implementer(IResponse)
class Success(Response):
    """ Response to be returned in the case of a successful
        request
    """

    def __init__(self, message):
        super(Success, self).__init__(message, True)


@implementer(IResponse)
class Fail(Response):
    """ Response to be returned in the case of a controled failure
    """

    def __init__(self, message):
        super(Fail, self).__init__(message, False)


@implementer(IResponse)
class Forbidden(Response):
    """ Response to be returned in the case of an attempt to access
        a restricted method
    """

    def __init__(self):
        super(Forbidden, self).__init__('FORBIDDEN', False)


@implementer(IResponse)
class InternalServerError(Response):
    """ Response to be returned in the case of an internal server error
    """

    def __init__(self):
        super(InternalServerError, self).__init__(
            'INTERNAL_SERVER_ERROR', False
        )
