# -*- coding: utf-8 -*-

import argparse
import glob
import os
import sys
import time
import unittest
from queue import Queue
from threading import Thread

from logbook import Logger
from plugins.your_plugin import *

from ziyan.lib.Sender import Sender
from ziyan.lib.Watchdog import watchdog, Maintainer
from ziyan.tests import Test_conf
from ziyan.utils.logbook_wrapper import setup_logger
from ziyan.utils.util import get_conf

log = Logger('start')


def start():
    # 队列初始化
    queue = {'command_queue': Queue(), 'data_queue': Queue(), 'sender': Queue()}

    all_conf = get_conf('conf/ziyan-main-conf.toml')

    user_conf = {}
    for conf in glob.glob('conf/*.toml'):
        if os.path.basename(conf) == 'ziyan-main-conf.toml':
            continue
        user_conf.update(get_conf(conf))

    all_conf['user_conf'] = user_conf

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

    thread_set = dict()

    recorder = Maintainer()

    for worker in workers:
        thread = Thread(target=worker.work, args=(queue,),
                        kwargs={'name': worker.name, 'record': recorder},
                        name='%s' % worker.name)
        thread.setDaemon(True)
        thread.start()
        thread_set[worker.name] = thread

    recorder.thread_set = thread_set

    watch = Thread(target=watchdog, name='watchdog', args=(thread_set, workers, queue, recorder))
    watch.setDaemon(True)
    watch.start()
    return recorder


def test():
    unittest.main(Test_conf, argv=sys.argv[1:])


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='A easy-to-use data collector with your device.')
    parse.add_argument('action', action='store')
    command = parse.parse_args().action
    if command == 'run':
        record = start()
        while True:
            record.protect()
            time.sleep(5)
    elif command == 'test':
        test()
