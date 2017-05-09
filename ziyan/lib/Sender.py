# -*- coding: utf-8 -*-
import time

import msgpack
import pendulum
from logbook import Logger

log = Logger('Sender')


class Sender:
    """
    用不同的databas wrapper，将数据以相应格式发送的sender
    """

    def __init__(self, configuration):
        self.to_where = configuration['sender']['send_to_where']
        self.lua_path = configuration['sender']['lua_path']

        if self.to_where == 'redis':
            from ziyan.utils.database_wrapper import RedisWrapper
            conf = configuration['sender']['redis']
            self.db = RedisWrapper(conf)

        # log format.
        self.enque_log_flag = configuration['sender']['enque_log']
        self.log_format = '\nmeasurement:{}\nunit:{}\ntimestamp:{}\ntags:{}\nfields:{}'
        pass

    def work(self, queue, **kwargs):
        """

        :param queue: format {'fields': {'Msg': '我是check的data'}, 
                            'timestamp': 1492572292, 'tags': {'eqpt_no': 'pec0-001', 'source': 's1'}, 
                            'measurement': 'test_measurement'}
        :return: None
        """

        sender_pipe = queue['sender']
        while True:
            data = sender_pipe.get()
            self.pack(data)

            kwargs['record'].thread_signal[kwargs['name']] = time.time()
        pass

    def send(self):
        """
        将队列里打包好的数据发送出去
        :return: 
        """
        pass

    def pack(self, data):
        """
        以发送的目标规定格式打包好数据

        :return: 
        """
        measurement = data['measurement']
        unit = data['unit']
        timestamp = data['timestamp']
        tags = data['tags']
        fields = data['fields']

        date_time = pendulum.from_timestamp(timestamp, tz='Asia/Shanghai').to_datetime_string()
        log_str = self.log_format.format(measurement, unit, date_time, tags, fields)
        if self.enque_log_flag:
            log.info(log_str)

        # for pack
        tags = msgpack.packb(tags)
        fields = msgpack.packb(fields)
        measurement = msgpack.packb(measurement)
        unit = msgpack.packb(unit)
        timestamp = msgpack.packb(timestamp)


        if self.to_where == 'redis':
            self.db.script_load(self.lua_path)
            lua_info = self.db.enqueue(timestamp=timestamp, tags=tags,
                                       fields=fields, measurement=measurement, unit=unit)
            log.info('\n' + lua_info.decode())
