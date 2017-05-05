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
                thread = threading.Thread(target=thread.work, args=(args[2],), kwargs={},
                                          name='%s' % thread.name, daemon=True)
                thread.start()
                threads_set[thread.name] = thread

            args[3].thread_set = threads_set

        time.sleep(10)
