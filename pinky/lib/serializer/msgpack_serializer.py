# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: json_serializer
    :platform: Unix, Windows
    :synopsys: JSON serializer module
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""
import umsgpack
from zope.interface import implementer

from pinky.lib.interfaces import ISerializer


@implementer(ISerializer)
class MSGPackSerializer(object):
    """ MSGPackSerializer is used to convert either the raw string raw form
        to a python data structure, or vise-versa.
        :Implements: `pinky.lib.interfaces.ISerializer`
        To binary Usage:
            data = {'key': 'some_value'}
            json_str = MSGPackSerializer(data).dump()
        From binary Usage:
            str = '{"key": "some_value"}'
            data = MSGPackSerializer(str).load()
    """

    @classmethod
    def dump(cls, content):
        """
        """
        if content is not None:
            return umsgpack.packb(content)

    @classmethod
    def load(cls, content):
        """
        """
        if content is not None:
            return umsgpack.unpackb(content)
