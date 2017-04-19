# encoding: utf-8

import argparse
import os
import traceback
import shutil
import glob


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
            # os.mkdir(name)
            os.makedirs(name + r'\conf')
            os.mkdir(name + r'\lua')
            os.mkdir(name + r'\plugins')
            filepath = os.path.split(os.path.realpath(__file__))[0]

            for file in glob.glob(filepath + r'\text_file\*.toml'):
                filename = os.path.join(filepath + '\\text_file\\', file)
                shutil.copy(filename, name + r'\conf\config.toml')

            for file in glob.glob(filepath + r'\text_file\*.lua'):
                filename = os.path.join(filepath + '\\text_file\\', file)
                shutil.copy(filename, name + r'\lua\enque_script.lua')

            shutil.copy(filepath+r'\script\manage.py', name + r'\manage.py')
    except Exception as e:
        traceback.print_exc()
