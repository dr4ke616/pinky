
# -*- coding: utf8 -*-
# Copyright (c) 2013 Dedsert Ltd.
# See LICENSE for more details

"""
.. module:: manhole
    :platform: Unix, Windows
    :synopsys: ManHole Administrative Python Shell

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>

"""

import string
from rlcompleter import Completer

from twisted.application import internet
from twisted.cred import portal, checkers
from twisted.conch import manhole, manhole_ssh


class EnhancedColoredManhole(manhole.ColoredManhole):

    def find_common(self, l):
        """
        Find common parts in thelist items ex: 'ab' for ['abcd','abce','abf']
        requires an ordered list
        """
        if len(l) == 1:
            return l[0]

        init = l[0]
        for item in l[1:]:
            for i, (x, y) in enumerate(zip(init, item)):
                if x != y:
                    init = "".join(init[:i])
                    break

            if not init:
                return None
        return init

    def handle_TAB(self):
        necessarypart = "".join(self.lineBuffer).split(' ')[-1]

        completer = Completer(globals())
        if completer.complete(necessarypart, 0):
            matches = list(set(completer.matches))  # has multiples
            if len(matches) == 1:
                length = len(necessarypart)
                self.lineBuffer = self.lineBuffer[:-length]
                self.lineBuffer.extend(matches[0])
                self.lineBufferIndex = len(self.lineBuffer)
            else:
                matches.sort()
                commons = self.find_common(matches)
                if commons:
                    length = len(necessarypart)
                    self.lineBuffer = self.lineBuffer[:-length]
                    self.lineBuffer.extend(commons)
                    self.lineBufferIndex = len(self.lineBuffer)
                self.terminal.nextLine()
                while matches:
                    matches, part = matches[4:], matches[:4]
                    for item in part:
                        self.terminal.write('%s' % item.ljust(30))
                    self.terminal.write('\n')
                self.terminal.nextLine()
            self.terminal.eraseLine()
            self.terminal.cursorBackward(self.lineBufferIndex + 5)
            self.terminal.write(
                "%s %s" % (self.ps[self.pn], "".join(self.lineBuffer))
            )

    def keystrokeReceived(self, keyID, modifier):
        # my terminal needed this
        self.keyHandlers.update({'\b': self.handle_BACKSPACE})
        m = self.keyHandlers.get(keyID)
        if m is not None:
            m()
        elif keyID in string.printable:
            self.characterReceived(keyID, False)


def get_manhole_factory(namespace, **passwords):
    """Get a Manhole Factory
    """

    realm = manhole_ssh.TerminalRealm()
    realm.chainedProtocolFactory.protocolFactory = (
        lambda _: EnhancedColoredManhole(namespace)
    )

    p = portal.Portal(realm)
    p.registerChecker(
        checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords)
    )
    return manhole_ssh.ConchFactory(p)


class ManholeServer(internet.TCPServer):
    def __init__(self, user, password, port):
        factory = get_manhole_factory(globals(), **{user: password})
        internet.TCPServer.__init__(self, int(port), factory)
