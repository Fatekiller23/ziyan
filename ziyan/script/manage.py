# -*- coding: utf-8 -*-

import argparse
from queue import Queue
from threading import Thread
from ziyan.lib.Sender import Sender
from ziyan.utils.util import get_conf
from plugins.plugin_prototype import *

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

def test():
    pass

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='This is a parse')
    parse.add_argument('action', action='store')
    command = parse.parse_args().action
    if command == 'run':
        start()
        while True:
            pass
    elif command == 'test':
        test()
