from __future__ import print_function

import os
import sys
import subprocess

from twisted.python import usage

from pinky.core.utils import get_host_address, get_available_port

from output import darkgreen, darkred
from utils import handle_stop_command, BaseStartOptions, BaseStopOptions

SERVICE = 'node'


class StartOptions(BaseStartOptions):
    """ Start command options for pinky-node tool
    """
    optParameters = [
        ['port', None, None,
            ('The port number to listen on. '
                'By default it will pick an available port')],
        ['host', None, None,
            ('The host address to bind to. '
                'By default try determine it by itself')],
        ['pidfile', None, '/var/run/pinky_node.pid',
            'File for the process Id.'],
        ['broker_host', 'h', None, 'The broker host to connect to.'],
        ['broker_port', 'p', 43435, 'The broker port to connect to.']
    ]


class StopOptions(BaseStopOptions):
    """ Start command options for pinky-broker tool
    """
    optParameters = [
        ['pidfile', None, '/var/run/pinky_node.pid',
            'File for the process Id.'],
    ]


class Options(usage.Options):
    """Base options for pinky-node tool
    """
    synopsis = 'Usage: pinky-node [options]'

    subCommands = [
        ['start', None, StartOptions, 'Start the pinky-node instance'],
        ['stop', None, StopOptions, 'Stop the pinky-node instance']
    ]

    def postOptions(self):
        """Post options processing
        """
        if len(sys.argv) == 1:
            print(self)


def handle_start_command(options):
    arguments = [
        'twistd', '--pidfile={}'.format(options.subOptions.opts['pidfile'])
    ]

    port = options.subOptions.opts['port'] or get_available_port()
    host = options.subOptions.opts['host'] or get_host_address()['ipv4']
    broker_host = options.subOptions.opts['broker_host']
    if not broker_host:
        print('You are missing the broker_host paramater'.ljust(73), end='')
        print('[{}]'.format(darkred('Fail')))
        print(options)
        sys.exit(1)

    nodaemon = options.subOptions.opts['nodaemon']
    if nodaemon:
        arguments.append('--nodaemon')
    else:
        arguments.append('--syslog')
        arguments.append('--prefix=pinky-node')

    arguments.append(SERVICE)
    arguments.append('--port={}'.format(port))
    arguments.append('--host={}'.format(host))
    arguments.append('--broker_host={}'.format(broker_host))

    if options.subOptions.opts['debug']:
        arguments.append('--debug')

    print('Starting pinky-node service'.ljust(73), end='')
    if nodaemon:
        os.execlp('twistd', *arguments)
    else:
        proc = subprocess.Popen(
            arguments,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = proc.communicate()
        if not err:
            if 'exception' in out:
                result = darkred('Fail')
                exit_code = -1
            else:
                result = darkgreen('Ok')
                exit_code = 0
        else:
            result = darkred('Fail')
            exit_code = -1

        print('[{}]'.format(result))
        print(err if exit_code == -1 else out)
        sys.exit(exit_code)


def run():

    try:
        options = Options()
        options.parseOptions()
    except usage.UsageError as errortext:
        print('{}: {}'.format(sys.argv[0], errortext))
        sys.exit(1)

    if options.subCommand == 'start':
        handle_start_command(options)

    if options.subCommand == 'stop':
        pidfile = options.subOptions.opts['pidfile']
        handle_stop_command(SERVICE, pidfile)


if __name__ == '__main__':
    run()
