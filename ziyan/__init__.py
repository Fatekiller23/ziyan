# encoding: utf-8

import argparse
import os
import traceback


def main():
    """
    Get the project name
    :return: None
    """
    namespace, project = argparse.ArgumentParser().parse_known_args()

    if project:
        if len(project) >= 2:
            print('error, just require one argument, but more')
        make_directory(project.pop())
    else:
        print('type project name, please')


def make_directory(name):
    """
    create a new project directory like follow:
    -name
    |
      -- conf\
    |
      -- lua\
    |
      -- plugins\
    |
      -- manage.py
    :param name: project name, str
    :return: None
    """
    try:
        if not os.path.exists(name):
            os.mkdir(name + r'\conf')
            os.mkdir(name + r'\lua')
            os.mkdir(name + r'\plugins')
            manage = open(name + r'\manage.py', 'w')
            conf = open(name + r'\conf\config.toml', 'w')
            manage.close()
            conf.close()
    except Exception as e:
        traceback.print_exc()
