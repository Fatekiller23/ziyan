# -*- coding: utf-8 -*-
import time
from queue import Queue
from threading import Thread

import pendulum
from lib.Sender import Sender

from ziyan.lib.Sender import Sender
from ziyan.utils.util import get_conf


class Command(object):
    def __init__(self, configuration):
        self.conf = configuration['command']

        # 类相关属性
        self.query_rate = self.conf['query_rate']
        pass

    def work(self, queues, **kwargs):
        # get command queue
        self.command_queue = command_queue = queues['command_queue']

        while True:
            # 使用用户逻辑创造command
            cmd = self.user_create_command()

            command_queue.put(cmd)

            # 查询频次，以秒为单位
            time.sleep(self.query_rate)

    def user_create_command(self):
        cmd = 1
        return cmd


class Check(object):
    data = '我是check的data'

    def __init__(self, configuration):
        self.conf = configuration['check']
        pass

    def work(self, queues, **kwargs):
        # 在实例中维持queue，待日后使用
        self.command_queue = command_queue = queues['command_queue']
        self.data_queue = data_queue = queues['data_queue']

        while True:
            # 获取命令
            cmd = command_queue.get()

            # 使用用户逻辑查询数据
            raw_data = self.user_check(cmd)

            # 将查询到的数据传至handler
            data_queue.put(raw_data)

    def user_check(self, command):

        if command == 1:
            return Check.data
        pass  # for debugging use.


class Handler(object):
    def __init__(self, configuration):
        self.conf = configuration['handler']
        self.make_processed_dict()
        self.field_name_list = self.conf['field_name_list']
        pass

    def work(self, queues, **kwargs):
        while True:
            self.data_queue = data_queue = queues['data_queue']
            raw_data = data_queue.get()
            processed_dict = self.user_handle(raw_data)
            self.enque_prepare(processed_dict)
            time.sleep(1)

    def enque_prepare(self, processed_dict):
        """
        
        :param processed_dict: 
        :return: fields, timestamp, tags, measurement
        """
        value_list = processed_dict.get('data_value')
        fields = dict(zip(self.field_name_list, value_list))

        # 从用户字典中获取时间，若没有，补充一个
        timestamp = processed_dict.get('timestamp', pendulum.now().int_timestamp)

        self.data_dict.update({'fields': fields, 'timestamp': timestamp})
        print(self.data_dict)
        pass

    # tag measurement
    def user_handle(self, raw_data):
        """
        用户须输出一个dict，可以填写一下键值，也可以不填写
        timestamp， 从数据中处理得到的时间戳（整形?）
        tags, 根据数据得到的tag
        data_value 数据拼成的list
        measurement 根据数据类型得到的 influxdb表明
        :param raw_data: 
        :return: 
        """
        # 数据经过处理之后生成 value_list
        data_value_list = [raw_data]

        tags = {'user_defined_tag': 'data_ralated_tag'}

        # user 可以在handle里自己按数据格式制定tags
        user_postprocessed = {'data_value': data_value_list,
                              'tags': tags, }
        return user_postprocessed

    def make_processed_dict(self, ):
        """
        在handler类初始化阶段，从配置文件中提取tag，measurement信息，
        注册在类信息中。
        :return: None 
        """
        tags = self.conf['tag']
        measurement = self.conf['measurement']
        self.data_dict = {'fields': None,
                          'tags': tags, 'measurement': measurement}


def start():
    # 队列初始化
    queue = {'command_queue': Queue(), 'data_queue': Queue()}
    all_conf = get_conf('text_file/configuration.toml')
    # 生成三个实例类
    commander = Command(all_conf)
    checker = Check(all_conf)
    handler = Handler(all_conf)
    sender = Sender()

    # 给实例赋名字
    commander.name = 'commander'
    checker.name = 'checker'
    handler.name = 'handler'

    # 用于迭代
    workers = [commander, checker, handler]

    for worker in workers:
        Thread(target=worker.work, args=(queue,), kwargs={'who': worker.name},
               name='t_%s' % worker.name, daemon=True).start()

        # 开启sender


if __name__ == '__main__':
    start()

    # keep main thread alive.
    while True:
        pass
