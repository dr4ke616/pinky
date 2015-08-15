# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: json_serializer
    :platform: Unix, Windows
    :synopsys: JSON serializer module
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""
import json
from decimal import Decimal
from zope.interface import implementer
from datetime import date, time, datetime

from pinky.core.interfaces import ISerializer

ISO_DATE_FMT = '%Y-%m-%d'
DATE_FMT = ISO_DATE_FMT


@implementer(ISerializer)
class JSONSerializer(object):
    """ JSONSerializer is used to convert either the raw string raw form
        to a python data structure, or vise-versa.
        :Implements: `pinky.core.interfaces.ISerializer`
        To JSON string Usage:
            data = {'key': 'some_value'}
            json_str = JSONSerializer(data).dump()
        From JSON string Usage:
            str = '{"key": "some_value"}'
            data = JSONSerializer(str).load()
    """

    @classmethod
    def dump(cls, content):
        """ Return string representation of JSON content
            or `None` if the contnet is null
        """
        if content is not None:
            return json.dumps(content, default=cls._serialize)

    @classmethod
    def load(cls, content):
        """ Return a Python data structure representation of JSON content
            or `None` if the contnet is null
        """
        if content is not None:
            return json.loads(content)

    @classmethod
    def _serialize(cls, obj):
        """ Private method to handle custom encoding for objects like `datetime`
            `Decimal`, etc
            :return: string representation of JSON data
            :raise TypeError: if JSON is not serializable
        """
        if hasattr(obj, 'json'):
            if callable(obj.json):
                return json.loads(obj.json())
            else:
                return json.loads(obj.json)
        elif isinstance(obj, datetime):
            return obj.date().strftime(
                DATE_FMT) + ' ' + obj.time().isoformat()
        elif isinstance(obj, date):
            return obj.strftime(ISO_DATE_FMT)
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        else:
            raise TypeError("Not JSON serializable: %s" % type(obj))
