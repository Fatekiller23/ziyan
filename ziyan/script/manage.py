# -*- coding: utf-8 -*-

import argparse
import glob
from queue import Queue
from threading import Thread

from plugins.plugin_prototype import *

from ziyan.lib.Sender import Sender
from ziyan.lib.Watchdog import watchdog
from ziyan.utils.logbook_wrapper import setup_logger
from ziyan.utils.util import get_conf


def start():
    # 队列初始化
    queue = {'command_queue': Queue(), 'data_queue': Queue(), 'sender': Queue()}

    all_conf = dict()
    for conf in glob.glob('conf/*.toml'):
        all_conf.update(get_conf(conf))

    # 日志生成初始化
    setup_logger(all_conf['log_configuration'])

    # 生成四个实例类
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

    thread_set = set()

    for worker in workers:
        thread = Thread(target=worker.work, args=(queue,), kwargs={},
                        name='%s' % worker.name, daemon=True)
        thread.start()
        thread_set.add(thread)

    Thread(target=watchdog, name='watchdog', args=(thread_set, workers, queue), daemon=True).start()


def test():
    pass


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='A easy-to-use data collector with your device.')
    parse.add_argument('action', action='store')
    command = parse.parse_args().action
    if command == 'run':
        start()
        while True:
            pass
    elif command == 'test':
        test()
