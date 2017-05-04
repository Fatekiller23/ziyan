# coding: utf-8

from setuptools import setup, find_packages

setup(
    name='ziyan',
    version='0.0.1',
    author='',
    author_email='',
    description='a easy-to-use data collector with your device.',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    license='MIT',
    install_requires=['pendulum', 'logbook', 'redis', 'influxdb', 'msgpack-python'],
    entry_points={
        'console_scripts': [
            'ziyan_make=ziyan:main'
        ]
    }
)
