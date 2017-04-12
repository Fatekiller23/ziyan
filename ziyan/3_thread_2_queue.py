# -*- coding: utf-8 -*-
import time
from queue import Queue
from threading import Thread


class Command(object):
    def __init__(self):
        pass

    def work(self, queues):
        while True:
            cmd = 1
            command_queue = queues['command_queue']
            command_queue.put(cmd)
            time.sleep(1)


class Check(object):
    data = '我是check的data'
    def __init__(self):

        pass

    def work(self, queues):
        while True:
            command_queue = queues['command_queue']
            data_queue = queues['data_queue']

            cmd = command_queue.get()
            if cmd == 1:
                data_queue.put(Check.data)


class Handler(object):
    def __init__(self):
        pass

    def work(self, queues):
        while True:
            data_queue = queues['data_queue']
            data = data_queue.get()
            print(data)


def start():
    q = {'command_queue': Queue(), 'data_queue': Queue()}

    commander = Command()
    checker = Check()
    handler = Handler()

    t1 = Thread(target=commander.work, args=(q,))
    t1.setDaemon(True)

    t2 = Thread(target=checker.work, args=(q,))
    t2.setDaemon(True)

    t3 = Thread(target=handler.work, args=(q,))
    t3.setDaemon(True)

    t1.start()
    t2.start()
    t3.start()


if __name__ == '__main__':
    start()
    while True:
        time.sleep(1)

