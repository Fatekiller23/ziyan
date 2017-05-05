# -*- coding: utf-8 -*-

import argparse
import ctypes
import datetime
import glob
import inspect
import os
import sys
import time
import unittest
from queue import Queue
from threading import Thread

from plugins.your_plugin import *

from ziyan.lib.Sender import Sender
from ziyan.lib.Watchdog import watchdog
from ziyan.tests import Test_conf
from ziyan.utils.logbook_wrapper import setup_logger
from ziyan.utils.util import get_conf


class Maintainer:
    pass


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

    for worker in workers:
        thread = Thread(target=worker.work, args=(queue,), kwargs={},
                        name='%s' % worker.name, daemon=True)
        thread.start()
        thread_set[worker.name] = thread

    recorder = Maintainer()
    recorder.thread_set = thread_set
    recorder.date = datetime.date.today()
    Thread(target=watchdog, name='watchdog', args=(thread_set, workers, queue, recorder), daemon=True).start()
    return recorder


def test():
    unittest.main(Test_conf, argv=sys.argv[1:])


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        """if it returns a number greater than one, you're in trouble,
        and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='A easy-to-use data collector with your device.')
    parse.add_argument('action', action='store')
    command = parse.parse_args().action
    if command == 'run':
        record = start()
        while True:
            if record.date != datetime.date.today():
                record.date = datetime.date.today()
                for thread in record.thread_set.values():
                    _async_raise(thread.ident, SystemExit)
            time.sleep(5)
    elif command == 'test':
        test()
