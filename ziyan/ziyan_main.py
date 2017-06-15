# -*- coding: utf-8 -*-

import time
import types

try:
    from queue import Queue
except:
    from Queue import Queue

from threading import Thread

import pendulum
from logbook import Logger

from ziyan.lib.Sender import Sender
from ziyan.utils.util import get_conf

log = Logger('main')


class Command(object):
    def __init__(self, configuration):
        self.conf = configuration

        # 类相关属性
        self.query_rate = self.conf['ziyan']['query_rate']
        pass

    def work(self, queues, **kwargs):
        # get command queue
        self.command_queue = command_queue = queues['command_queue']

        while True:
            # 使用用户逻辑创造command
            cmd = self.user_create_command()

            if cmd:
                command_queue.put(cmd)
            else:
                log.error('\nNo command send')

            kwargs['record'].thread_signal[kwargs['name']] = time.time()

            # 查询频次，以秒为单位
            time.sleep(self.query_rate)

    def user_create_command(self):
        """
        base function
        :return: 
        """
        pass


class Check(object):
    data = '我是check的data'

    def __init__(self, configuration):
        self.conf = configuration
        pass

    def work(self, queues, **kwargs):
        # 在实例中维持queue，待日后使用
        self.command_queue = command_queue = queues['command_queue']
        self.data_queue = data_queue = queues['data_queue']

        while True:
            # 获取命令
            cmd = command_queue.get()

            # 使用用户逻辑查询数据
            if cmd:
                raw_datas = self.user_check(cmd)

                if isinstance(raw_datas, types.GeneratorType):
                    for raw_data in raw_datas:
                        # 将查询到的数据传至handler
                        data_queue.put(raw_data)
                else:
                    # 将查询到的数据传至handler
                    data_queue.put(raw_datas)
            else:
                log.error('\nNo command received')

            kwargs['record'].thread_signal[kwargs['name']] = time.time()

    def user_check(self, command):
        """
        base function
        :param command: 
        :return: 
        """
        pass


class Handler(object):
    def __init__(self, configuration):
        self.conf = configuration
        self.make_processed_dict()
        self.field_name_list = configuration['user_conf']['handler']['field_name_list']
        self.unit = configuration['ziyan'].get('unit', 's')
        self.data_dict['unit'] = self.unit

        pass

    def work(self, queues, **kwargs):
        while True:
            self.data_queue = data_queue = queues['data_queue']
            self.sender_pipe = queues['sender']
            raw_data = data_queue.get()

            if raw_data:
                processed_dicts = self.user_handle(raw_data)
                self.enque_prepare(processed_dicts)
            else:
                log.error('\nNo data is received')

            kwargs['record'].thread_signal[kwargs['name']] = time.time()

            time.sleep(1)

    def enque_prepare(self, processed_dicts):
        """

        :param processed_dicts: 
        :return: fields, timestamp, tags, measurement
        """
        if isinstance(processed_dicts, (types.GeneratorType, list)):
            for processed_dict in processed_dicts:

                # make fields.
                value_list = processed_dict.get('data_value')

                # user field list
                if not isinstance(value_list, dict):
                    fields = dict(zip(self.field_name_list, value_list))
                else:
                    fields = value_list

                # user tags
                tags = processed_dict.get('tags', None)

                # user measurement
                measurement = processed_dict.get('measurement', None)

                # 从用户字典中获取时间，若没有，补充一个
                if self.unit == 's':
                    timestamp = processed_dict.get('timestamp') or pendulum.now().int_timestamp
                else:
                    timestamp = processed_dict.get('timestamp') or int(pendulum.now().float_timestamp * 1000000)

                update_dict = {'fields': fields, 'timestamp': timestamp}

                # 补充用户自定义tag，measurement.
                if tags:
                    update_dict['tags'] = tags
                if measurement:
                    update_dict['measurement'] = measurement

                # 复制初始数据字典
                data = dict(self.data_dict)

                # 数据更新
                data.update(update_dict)
                self.sender_pipe.put(data)

        elif isinstance(processed_dicts, dict):

            # make fields.
            value_list = processed_dicts.get('data_value')
            fields = dict(zip(self.field_name_list, value_list))

            # user tags
            tags = processed_dicts.get('tags', None)

            # user measurement
            measurement = processed_dicts.get('measurement', None)

            # 从用户字典中获取时间，若没有，补充一个
            if self.unit == 's':
                timestamp = processed_dicts.get('timestamp') or pendulum.now().int_timestamp
            else:
                timestamp = processed_dicts.get('timestamp') or int(pendulum.now().float_timestamp * 1000000)

            update_dict = {'fields': fields, 'timestamp': timestamp}

            # 补充用户自定义tag，measurement.
            if tags:
                update_dict['tags'] = tags
            if measurement:
                update_dict['measuremement'] = measurement

            # 复制初始数据字典
            data = dict(self.data_dict)

            # 数据更新
            data.update(update_dict)
            self.sender_pipe.put(data)

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
        pass

    def make_processed_dict(self, ):
        """
        在handler类初始化阶段，从配置文件中提取tag，measurement信息，
        注册在类信息中。
        :return: None 
        """
        tags = self.conf['user_conf']['handler']['tag']
        measurement = self.conf['user_conf']['handler']['measurement']
        self.data_dict = {'fields': None,
                          'tags': tags, 'measurement': measurement}


def start():
    # 队列初始化
    queue = {'command_queue': Queue(), 'data_queue': Queue(), 'sender': Queue()}
    all_conf = get_conf('text_file/ziyan-main-conf.toml')
    # 生成三个实例类
    commander = Command(all_conf)
    checker = Check(all_conf)
    handler = Handler(all_conf)
    sender = Sender(all_conf)

    # 给实例赋名字
    commander.name = 'commander'
    checker.name = 'checker'
    handler.name = 'handler'
    sender.name = 'sender'

    # 用于迭代
    workers = [commander, checker, handler, sender]

    for worker in workers:
        Thread(target=worker.work, args=(queue,), kwargs={'who': worker.name},
               name='t_%s' % worker.name, daemon=True).start()


if __name__ == '__main__':
    start()

    # keep main thread alive.
    while True:
        pass
