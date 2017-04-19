# coding: utf-8

from setuptools import setup

setup(
    name='ziyan',
    version='0.0.1',
    author='',
    author_email='',
    description='a easy-to-use data collector with your device.',
    packages=['ziyan'],
    license='MIT',
    install_requires=['pendulum', 'logbook', 'redis', 'influxdb'],
    entry_points={
        'console_scripts': [
            'ziyan_make=ziyan:main'
        ]
    }
)
