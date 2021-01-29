#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import re
from setuptools import setup, find_packages

# Python versions this package is compatible with
python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4'

# Packages that this package imports. List everything apart from standard lib packages.
install_requires = [
    'sensirion-i2c-driver~=1.0.0',
    'enum34;python_version<"3.4"',
]

# Packages required for tests and docs
extras_require = {
    'test': [
        'flake8~=3.7.8',
        'pytest~=3.5.0',
        'pytest-cov~=2.5.1',
        'sensirion-shdlc-sensorbridge~=0.1.1'
    ],
    'docs': [
        'sphinx~=2.2.1',
        'sphinx-rtd-theme~=0.4.3',
    ]
}

# Packages only required to run this setup file.
setup_requires = [
    'pytest-runner~=4.2',
]


# Read version number from version.py
version_line = open("sensirion_i2c_scd/version.py", "rt").read()
result = re.search(r"^version = ['\"]([^'\"]*)['\"]", version_line, re.M)
if result:
    version_string = result.group(1)
else:
    raise RuntimeError("Unable to find version string")


# Use README.rst and CHANGELOG.rst as package description
root_path = os.path.dirname(__file__)
readme = open(os.path.join(root_path, 'README.rst')).read()
changelog = open(os.path.join(root_path, 'CHANGELOG.rst')).read()
long_description = readme.strip() + "\n\n" + changelog.strip() + "\n"


setup(
    name='sensirion-i2c-scd',
    version=version_string,
    author='Pascal Sachs',
    author_email='pascal.sachs@sensirion.com',
    description='I2C driver for the Sensirion CO2 Sensor SCD4x',
    license='BSD',
    keywords='I2C SCD4x SCD41 Sensirion',
    url='http://developers.sensirion.com',
    packages=find_packages(exclude=['tests', 'tests.*']),
    long_description=long_description,
    python_requires=python_requires,
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require=extras_require,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
