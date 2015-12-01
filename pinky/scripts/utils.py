from __future__ import print_function

import os
import sys
import signal
import socket

from output import darkgreen, darkred
from twisted.python import filepath, usage


class BaseStartOptions(usage.Options):
    """ Base Start command options
    """
    synopsis = '[options]'

    optFlags = [
        ['debug', 'b', 'Enable/disable debug mode.'],
        ['nodaemon', 'n', 'don\'t daemonise the process.']
    ]

    def postOptions(self):
        """Post options processing
        """
        if len(sys.argv) == 3 and sys.argv[2] == '--help':
            print(self)


class BaseStopOptions(usage.Options):
    """ Base Stop command options
    """
    synopsis = '[options]'

    def postOptions(self):
        """Post options processing
        """
        if len(sys.argv) == 3 and sys.argv[2] == '--help':
            print(self)


def handle_stop_command(srv, pid):
    """ Kill the running service
        :param srv: `str` containing the service to kill
            passed in as underscore_case
    """
    service = 'pinky_{}'.format(srv)
    twisted_pid = filepath.FilePath(pid)
    if not twisted_pid.exists():
        print('error: {}.pid file can\'t be found.'.format(service))
        sys.exit(-1)

    pid = twisted_pid.open().read()
    print('killing {} process id {} with SIGINT signal'.format(
        service, pid).ljust(73), end='')
    try:
        filepath.os.kill(int(pid), signal.SIGINT)
        print('[{}]'.format(darkgreen('Ok')))
    except:
        print('[{}]'.format(darkred('Fail')))
        raise


def get_available_port():
    """ Complete hack. Some operating systems may not release
        the file descriptor straight away. So it will fail to
        bind when creating the node server itself.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_host_address():
    """ Another complete hack. Get the host IP address
    """
    ips = os.popen(
        "ip addr show eth0 | awk '/inet/ {print $2}' | cut -d/ -f1"
    ).read().split('\n')
    return {'ipv4': ips[0], 'ipv6': ips[1]}
