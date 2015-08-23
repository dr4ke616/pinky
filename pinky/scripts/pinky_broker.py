from __future__ import print_function

import os
import sys
import signal
import subprocess

from output import darkgreen, darkred
from twisted.python import usage, filepath


class StartOptions(usage.Options):
    """Start command options for mamba-admin tool
    """
    synopsis = '[options]'

    optParameters = [
        ['port', 'p', 43435, 'The port number to listen on.'],
        ['host', 'h', '0.0.0.0', 'The host to run on.']
    ]

    optFlags = [
        ['debug', 'b', 'Enable/disable debug mode.'],
        ['nodaemon', 'n', 'don\'t daemonise the process.']
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
        arguments.append('--pidfile=/var/run/pinky_broker.pid')
        arguments.append('--prefix=pinky-broker')

    arguments.append('broker')

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


def handle_stop_command():
    twisted_pid = filepath.FilePath('pinky_broker.pid')
    if not twisted_pid.exists():
        twisted_pid = filepath.FilePath('/var/run/pinky_broker.pid')
        if not twisted_pid.exists():
            print('error: pinky_broker.pid file can\'t be found.')
            sys.exit(-1)

    pid = twisted_pid.open().read()
    print('killing pinky-broker process id {} with SIGINT signal'.format(
        pid).ljust(73), end='')
    try:
        filepath.os.kill(int(pid), signal.SIGINT)
        print('[{}]'.format(darkgreen('Ok')))
    except:
        print('[{}]'.format(darkred('Fail')))
        raise


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
        handle_stop_command()


if __name__ == '__main__':
    run()
