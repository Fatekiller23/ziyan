# -*- coding:utf-8 -*-

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
    threads_name = {thread.name for thread in args[0]}
    while True:

        threads = set()

        for item in threading.enumerate():
            threads.add(item.name)

        log.debug('\n' + str(threads) + '\n')

        if threads - {'watchdog', 'MainThread'} != threads_name:
            dead_threads = threads_name - (threads - {'watchdog', 'MainThread'})

            # 获取死去线程的实例集
            dead_threads = [thread for thread in args[1] if thread.name in dead_threads]

            for thread in dead_threads:
                threading.Thread(target=thread.work, args=(args[2],), kwargs={},
                                 name='%s' % thread.name, daemon=True).start()

        time.sleep(10)
