# -*- coding:utf-8 -*-

import ctypes
import hashlib
import inspect
import os
import threading
import time

from logbook import Logger

log = Logger('watchdog')


def watchdog(*args):
    """
    守护线程
    :param args:
        args[0]: dict, key:thread_name, value:thread_instance
        args[1]: function, 重新生成类实例的方法
        args[2]: dict, 线程间通信的 queue 集合
        args[3]: 运行时的 Maintainer 的唯一实例
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
            # 重新加载配置文件
            dead_threads = [thread for thread in args[1](True) if thread.name in dead_threads]

            threads_set = dict()

            for thread in dead_threads:
                worker = threading.Thread(target=thread.work, args=(args[2],),
                                          kwargs={'name': thread.name, 'record': args[3]},
                                          name='%s' % thread.name)
                worker.setDaemon(True)
                worker.start()
                threads_set[thread.name] = worker

            args[3].thread_set.update(threads_set)

        time.sleep(10)


class Maintainer:
    def __init__(self):
        self.thread_signal = dict()
        self.thread_set = None
        self.sha = self.get_sha()

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

    def protect(self):
        for threadname, singal in self.thread_signal.items():

            # 判断是否存在线程僵死，如果存在，kill 掉
            if time.time() - singal > 1200:
                try:
                    self._async_raise(self.thread_set[threadname].ident, SystemExit)
                    log.warning("\n%s is timeout, kill it" % threadname)
                    self.thread_signal[threadname] = time.time()
                except Exception as e:
                    log.error('\nThere is something wrong')

        # 判断文件是否更改，如果更改，将监控的所有线程 kill 掉
        if self.get_sha() != self.sha:
            log.warning("\nFile changes, program restart")

            for thread in self.thread_set.values():
                try:
                    self._async_raise(thread.ident, SystemExit)
                except Exception as e:
                    log.error('\nThere is something wrong on sha')

            self.sha = self.get_sha()

    def get_sha(self):
        """
        组成一个 元素为 tuple 的列表，tuple的值为 {文件路径, 文件的最后修改时间}，
        根据这个列表生成一个唯一 SHA 值
        :return: SHA 值
        """
        data = {}
        files = self.get_file_list()

        for file in files:
            if file[file.rfind('.') + 1:] in ['py', 'lua', 'toml']:
                data[file] = os.stat(file).st_mtime

        data = sorted(data.items(), key=lambda d: d[0])
        sha = hashlib.sha1(str(data).encode())
        return sha.hexdigest()

    @staticmethod
    def get_file_list(l='.', filelist=list()):
        """
        递归遍历工作目录，获取目录下的配置文件、python 文件、lua 文件列表
        :param l:
        :param filelist:
        :return: list
        """
        new_dir = l
        if os.path.isfile(l):
            filelist.append(l)
        elif os.path.isdir(l):
            for s in os.listdir(l):
                # 如果需要忽略某些文件夹，使用以下代码
                if s in ["logs", ".idea"]:
                    continue
                new_dir = os.path.join(l, s)
                Maintainer.get_file_list(new_dir, filelist)
        return filelist
