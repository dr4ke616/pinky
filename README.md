# Pinky

Pinky is a multi node distributed replicated in memory cache application. The name Pinky comes from [Pink & The Brain](https://www.google.com/search?q=Pinky+%26+The+Brain), Pinky being the dopey character.

[![Build Status](https://travis-ci.org/dr4ke616/pinky.svg?branch=master)](https://travis-ci.org/dr4ke616/pinky)

## How not to create distributed in memory cache

`Pinky` is a single broker, multi node distributed replicated in memory cache application. This is a very simple and basic implementation that was intended for experimental purposes only. This is not intended to be used in production. `Pinky` is designed using a central broker architecture, with one or more nodes registered to the broker. `Pinky` is fully asynchronous - written in Python using the [Twisted](http://twistedmatrix.com/) framework with [ZeroMQ](http://zeromq.org/). This project was intended to gain a better understanding of `ZeroMQ` with `Twisted`.

I've realised that this architecture is fundamentally flawed. With the broker being the central point of failure, regarding all input and output communication with a given cluster as well as the main register for all of the nodes, if the broker goes down - we loose communication to all nodes. Alternative interesting architectures that are commonly used through out the `ZeroMQ` community are all outlined [here](http://zeromq.org/whitepapers:brokerless).

## Installation

Install using pip
```bash
$ pip install txpinky
```

If you just want to install from source
```bash
$ git clone http://github.com/dr4ke616/pinky.git && cd pinky/
$ python setup.py install
```

Or if you want to mess around or even contribute
```bash
$ git clone http://github.com/dr4ke616/pinky.git && cd pinky/
$ pip install -r requirements.txt
$ ./run_tests  # Run the tests
```

## Usage
Once Pinky is installed correctly, you should have two command line tools `pinky-broker` and `pinky-node` available in your path. Use `--help` for info on these.

### pinky-broker

Start an instance of the central broker `pinky-broker start`. Some arguments available are:
* `--port`: Set the port for `pinky-broker` to listen on. By default it will listen on `43435`.
* `--pidfile`: Use this to set the location for the `pid` file. By default this will be `/var/run/pinky_broker.pid`. This will need root access.
* `--activate-ssh-server`: This is an interesting one. Pinky comes with its own internal SSH server you can activate with this argument. By default it is not activated. Read below to find more info on this. If this is enabled, you will need to set the next three arguments.
* `--ssh-user`: A user you want to login with.
* `--ssh-password`: A password to login with using the above user.
* `--ssh-port`: A port to listen on.

To stop the broker, just run `pinky-broker stop`.
* `--pidfile`: If the `pid` file was set to a different location than the default when starting, you will need to tell the stop command where it is.

### pinky-node

Start one or more nodes.
* `-h` `--broker_host`: The location of the central broker.
* `-p` `--broker_port`: The port for the central broker. By default it will be `43435`
* `--port`: Set the port for `pinky-node` to listen on. By default it will try pick an available port.
* `--pidfile`: Use this to set the location for the `pid` file. By default this will be `/var/run/pinky_node.pid`. This will need root access.

To stop a node, just run `pinky-node stop`.
* `--pidfile`: If the `pid` file was set to a different location than the default when starting, you will need to tell the stop command where it is.

### SSH Interface

When you activate the SSH service within the broker, you can login like you would any other SSH server:
```
$ ssh -P 4567 foo@localhost
foo@localhost's password:
>>>
```

Once you gain access, you will be presented with a Python REPL. Here you can import any module and run any action on the running instance. This is a pretty basic SSH service, there is currently no support for multiple users or SSH keys. However it is a great way to explore the data currently stored within the cluster. This can be done as follows:
```python
>>> from pinky.core.utils import get_host_address
>>> from pinky.broker.client import BrokerClient
>>> cl = BrokerClient.create('tcp://{}:43435'.format(get_host_address()['ipv4']))
>>> cl.keys('*')
>>> cl.set('some_key', 'some_value')
>>> cl.get('some_key')
```

Note: because we are connected straight to the broker application, we can utilise a function `get_host_address` to get the host IP address the broker is running on. This returns a dictionary containing an `ipv4` and `ipv6` address. In this case we only care about the `ipv4` address.

### Docker

`Pinky` comes with [Docker](https://www.docker.com/) files. It is presumed that you have the latest version of Docker installed.

To build the Docker images you first need to build a base Docker image, then the Broker and the Node:
```bash
$ docker build --rm --tag=pinky-base:0.10 --file="docker/base" .
$ docker build --rm --tag=pinky-broker:0.10 --file="docker/broker" .
$ docker build --rm --tag=pinky-node:0.10 --file="docker/node" .
```

Once the Docker images are successfully built, you can run them.

The broker, by default this will also start a SSH server directly to the broker application. This allows you to ssh directly to it via `ssh admin@<docker_broker_host_ip>`
```bash
$ docker run pinky-broker:0.10
```

Then one or more nodes. You need to determine the IP address for the broker's Docker container to set `BROKER_HOST` environment variable.
```bash
$ docker run -e "BROKER_HOST=<docker_broker_host_ip>" pinky-node:0.10
```

## TODO
- Separate `pinky-cli` that can provide a REPL and public APIs through a Python SDK.
- Handle some errors more appropriately.
- Look to move SSH users/password to some form of database, rather than being passed into the `pinky-broker start` command.

## Known Issues
- Needs the presence of the twisted directory for the plugins to work. Need to figure out a solution so that `twistd` command line tool sees this directory. Currently `pip` installed versions of `pinky` will not work by itself.
