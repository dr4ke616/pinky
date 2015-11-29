#!/usr/bin/env python
# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

""" Distutils installer for Pinky.
"""

import sys

if not hasattr(sys, "version_info") or sys.version_info < (2, 7):
    raise RuntimeError("Pinky requires Python 2.7 or later.")

from setuptools import setup, find_packages  # noqa

setup(
    name='txpinky',
    version='0.1.0',
    description=(
        'Pinky is a multi node distributed replicated '
        'in memory cache application.'
    ),
    author='Adam Drakeford',
    author_email='adamdrakeford@gmail.com',
    url='https://github.com/dr4ke616/pinky',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'twisted>=15.4.0', 'pyasn1>=0.1.9', 'pycrypto>=2.6.1', 'setuptools',
        'pyzmq>=15.0.0', 'txZMQ>=0.7.4', 'u-msgpack-python>=2.1'
    ],
    entry_points={
        'console_scripts': [
            'pinky-broker = pinky.scripts.pinky_broker:run',
            'pinky-node = pinky.scripts.pinky_node:run'
        ]
    },
    zip_safe=False,
    classifiers=[
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
