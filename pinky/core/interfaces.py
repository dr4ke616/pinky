# Copyright (c) 2015 Adam Drakeford <adam.drakeford@betbright.com>
# See LICENSE for more details

"""
.. module:: interfaces
    :platform: Unix, Windows
    :synopsys: Interfaces module
.. moduleauthor:: Adam Drakeford <adam.drakeford@betbright.com>
"""

from zope.interface import Interface, Attribute


class ISerializer(Interface):

    def __init__(content):
        """ The object needs to be initalised with the data content
        """

    def dump(content):
        """ Method to dump the contents of `content` using what ever
            data structure defined in the class, for example could be XML,
            JSON, Yaml, etc. This method is expected to return the string
            representation of the encoded data
        """

    def load(content):
        """ Method to load the contents of `content` using what ever
            data structure defined in the class, for example could be XML,
            JSON, Yaml, etc. This method is expected to return a data
            structure best suited for the class.
        """


class IResponse(Interface):
    """
    Pinky Response interface. Every response from a given server
    must implement this interface
    """

    success = Attribute(
        """
        :param success: Success indicator
        :type success: bool
        """
    )

    message = Attribute(
        """
        :param message: Message to be sent back
        :type success: string/dict/list
        """
    )


class IStorage(Interface):

    def set(key, value):
        """ Set the string value of a string
        """

    def get(key):
        """ Get a value of a key
        """

    def mget(keys):
        """ Get the values of all given keys
        """

    def delete(key):
        """ Delete a key
        """

    def keys(pattern):
        """ Find all keys matching a given pattern
        """
