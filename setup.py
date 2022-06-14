#!/usr/bin/env python
"""Setup installer for Fido."""
# -*- coding: utf-8 -*-

import fastapi
from setuptools import setup, find_packages


install_requires = [
    'setuptools',
    'importlib_resources',
    'fastapi',
]


setup_requires = [
    'pytest-runner',
]


tests_require = [
    'pytest', 'flake8', 'pep257', 'pytest-cov', 'pylint'
]

EXTRAS = {
    'testing': tests_require,
    'setup': setup_requires,
}
PYTHON_REQUIRES = '>=3.9, <4'

setup(
    name='fidosigs',
    version='1.0a1',
    packages=find_packages(),
    include_package_data=True,
    description='Format Identification for Digital Objects (FIDO) signature update service.',
    long_description='A set of web services to update FIDO signatures. FIDO uses the UK National Archives (TNA) PRONOM File Format and Container descriptions.',
    author='Carl Wilson (OPF), 2022',
    url='http://openpreservation.org/technology/products/fido/',
    license='Apache License 2.0',
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require=EXTRAS,
    platforms=['POSIX'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ]
)
