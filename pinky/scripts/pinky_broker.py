from __future__ import print_function

import os
import sys
import subprocess

from twisted.python import usage
from output import darkgreen, darkred
from utils import handle_stop_command, BaseStartOptions

SERVICE = 'broker'


class StartOptions(BaseStartOptions):
    """ Start command options for pinky-broker tool
    """
    optParameters = [
        ['port', 'p', 43435, 'The port number to listen on.']
    ]


class Options(usage.Options):
    """Base options for pinky-broker tool
    """
    synopsis = 'Usage: pinky-broker [options]'

    subCommands = [
        ['start', None, StartOptions, 'Start the pinky-broker instance'],
        ['stop', None, usage.Options, 'Stop the pinky-broker instance']
    ]

    def postOptions(self):
        """Post options processing
        """
        if len(sys.argv) == 1:
            print(self)


def handle_start_command(options):
    arguments = ['twistd']

    nodaemon = options.subOptions.opts['nodaemon']
    if nodaemon:
        arguments.append('--nodaemon')
        arguments.append('--pidfile=pinky_broker.pid')
    else:
        arguments.append('--syslog')
        # arguments.append('--pidfile=/var/run/{}.pid'.format(service))
        arguments.append('--pidfile=pinky_broker.pid')
        arguments.append('--prefix=pinky-broker')

    arguments.append(SERVICE)

    if options.subOptions.opts['debug']:
        arguments.append('--debug')

    print('Starting pinky-broker service'.ljust(73), end='')
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
        handle_stop_command(SERVICE)


if __name__ == '__main__':
    run()