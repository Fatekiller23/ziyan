# encoding: utf-8

import argparse
import glob
import os
import shutil
import traceback
from queue import Queue
from threading import Thread

from ziyan.lib.Sender import Sender
from ziyan.plugins.plugin_prototype import *
from ziyan.utils.util import get_conf


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

            shutil.copy(filepath + r'\script\manage.py', name + r'\manage.py')
    except Exception as e:
        traceback.print_exc()


def start():
    # 队列初始化
    queue = {'command_queue': Queue(), 'data_queue': Queue(), 'sender': Queue()}
    all_conf = get_conf('conf/config.toml')
    # 生成三个实例类
    commander = MyCommand(all_conf)
    checker = MyCheck(all_conf)
    handler = MyHandler(all_conf)
    sender = Sender(all_conf)

    # 给实例赋名字
    commander.name = 'commander'
    checker.name = 'checker'
    handler.name = 'handler'
    sender.name = 'sender'

    # 用于迭代
    workers = [commander, checker, handler, sender]

    for worker in workers:
        Thread(target=worker.work, args=(queue,), kwargs={'who': worker.name},
               name='t_%s' % worker.name, daemon=True).start()
