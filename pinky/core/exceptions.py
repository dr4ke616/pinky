import re


class PinkyException(Exception):

    @property
    def code(self):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.__class__.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()


class NodeRegisterFailed(PinkyException):
    pass


class ZeroNodes(PinkyException):
    pass
