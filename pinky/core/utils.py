# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: utils
    :platform: Unix, Windows
    :synopsys: generic utilities
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import os
import socket


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
