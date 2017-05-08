# -*- coding:utf-8 -*-

import ctypes
import inspect
import threading
import time

from logbook import Logger

log = Logger('watchdog')


def watchdog(*args):
    """
    守护线程
    :param args: 
    :return: None
    """
    threads_name = {thread.name for thread in args[0].values()}
    while True:

        threads = set()

        for item in threading.enumerate():
            threads.add(item.name)

        log.debug('\n' + str(threads) + '\n')

        if threads - {'watchdog', 'MainThread'} != threads_name:
            dead_threads = threads_name - (threads - {'watchdog', 'MainThread'})

            # 获取死去线程的实例集
            dead_threads = [thread for thread in args[1] if thread.name in dead_threads]

            threads_set = dict()

            for thread in dead_threads:
                worker = threading.Thread(target=thread.work, args=(args[2],),
                                          kwargs={'name': thread.name, 'record': args[3]},
                                          name='%s' % thread.name)
                worker.setDaemon(True)
                worker.start()
                threads_set[thread.name] = worker

            args[3].thread_set = threads_set

        time.sleep(10)


class Maintainer:
    def __init__(self):
        self.thread_signal = dict()
        self.thread_set = None

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            log.error("invalid thread id")
        elif res != 1:
            """if it returns a number greater than one, you're in trouble,
            and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            log.error("PyThreadState_SetAsyncExc failed")

    def project(self):
        for threadname, singal in self.thread_signal.items():
            if time.time() - singal > 1200:
                try:
                    self._async_raise(self.thread_set[threadname].ident, SystemExit)
                except Exception as e:
                    log.error('\nThere is something wrong')
