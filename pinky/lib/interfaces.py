# Copyright (c) 2015 Adam Drakeford <adam.drakeford@betbright.com>
# See LICENSE for more details

"""
.. module:: interfaces
    :platform: Unix, Windows
    :synopsys: Interfaces module
.. moduleauthor:: Adam Drakeford <adam.drakeford@betbright.com>
"""

from zope.interface import Interface


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
