from __future__ import print_function

import os
import sys
import subprocess

from twisted.python import usage
from output import darkgreen, darkred
from utils import handle_stop_command, BaseStartOptions, BaseStopOptions

SERVICE = 'broker'


class StartOptions(BaseStartOptions):
    """ Start command options for pinky-broker tool
    """
    optParameters = [
        ['port', None, 43435, 'The port number to listen on.'],
        ['pidfile', None, '/var/run/pinky_broker.pid',
            'File for the process Id.'],
        ['activate-ssh-server', None, False,
            'Activate an SSH server on the broker for live debuging.'],
        ['ssh-user', None, None, 'SSH username.'],
        ['ssh-password', None, None, 'SSH pasword.'],
        ['ssh-port', None, None, 'SSH port to listen on.']
    ]


class StopOptions(BaseStopOptions):
    """ Start command options for pinky-broker tool
    """
    optParameters = [
        ['pidfile', None, '/var/run/pinky_broker.pid',
            'File for the process Id.'],
    ]


class Options(usage.Options):
    """Base options for pinky-broker tool
    """
    synopsis = 'Usage: pinky-broker [options]'

    subCommands = [
        ['start', None, StartOptions, 'Start the pinky-broker instance'],
        ['stop', None, StopOptions, 'Stop the pinky-broker instance']
    ]

    def postOptions(self):
        """Post options processing
        """
        if len(sys.argv) == 1:
            print(self)


def _handle_manhole(user, password, port, arguments):
    if None in (user, password, port):
        print(
            'You need to secify SSH user, password and port to activate it'
            ''.ljust(73), end=''
        )
        print('[{}]'.format(darkred('Fail')))
        sys.exit(1)

    arguments.append('--activate-ssh-server=true')
    arguments.append('--ssh-user={}'.format(user))
    arguments.append('--ssh-password={}'.format(password))
    arguments.append('--ssh-port={}'.format(port))


def handle_start_command(options):
    arguments = [
        'twistd', '--pidfile={}'.format(options.subOptions.opts['pidfile'])
    ]

    nodaemon = options.subOptions.opts['nodaemon']
    if nodaemon:
        arguments.append('--nodaemon')
    else:
        arguments.append('--syslog')
        arguments.append('--prefix=pinky-broker')

    arguments.append(SERVICE)

    if options.subOptions.opts['debug']:
        arguments.append('--debug')

    if options.subOptions.opts['activate-ssh-server']:
        _handle_manhole(
            options.subOptions.opts['ssh-user'],
            options.subOptions.opts['ssh-password'],
            options.subOptions.opts['ssh-port'],
            arguments
        )

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
        pidfile = options.subOptions.opts['pidfile']
        handle_stop_command(SERVICE, pidfile)


if __name__ == '__main__':
    run()
