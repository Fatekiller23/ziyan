# -*- coding: utf-8 -*-
import time
from queue import Queue
from threading import Thread


class Command(object):
    def __init__(self):
        pass

    def work(self, queues, **kwargs):
        while True:
            cmd = 1
            command_queue = queues['command_queue']
            command_queue.put(cmd)
            time.sleep(1)

    def user_logic(self):
        pass

class Check(object):
    data = '我是check的data'

    def __init__(self):
        pass

    def work(self, queues, **kwargs):
        while True:
            command_queue = queues['command_queue']
            data_queue = queues['data_queue']

            cmd = command_queue.get()
            if cmd == 1:
                data_queue.put(Check.data)

    def user_logic(self):
        pass

class Handler(object):
    def __init__(self):
        pass

    def work(self, queues, **kwargs):
        while True:
            data_queue = queues['data_queue']
            data = data_queue.get()
            print(data)

    def user_logic(self):
        pass

def start():
    queue = {'command_queue': Queue(), 'data_queue': Queue()}

    commander = Command()
    checker = Check()
    handler = Handler()

    commander.name = 'commander'
    checker.name = 'checker'
    handler.name = 'handler'

    workers = [commander, checker, handler]

    for worker in workers:
        Thread(target=worker.work, args=(queue,), kwargs={'who': worker.name},
               name='t_%s' % worker.name, daemon=True).start()


if __name__ == '__main__':
    start()
    while True:
        time.sleep(1)
