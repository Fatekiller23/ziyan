# -*- coding: utf-8 -*-
import time

import msgpack
import pendulum
from logbook import Logger

from ziyan.utils.database_wrapper import SqliteWrapper

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
            self.db.script_load(self.lua_path)

        elif self.to_where == 'influxdb':
            from ziyan.utils.database_wrapper import InfluxdbWrapper
            conf = configuration['sender']['influxdb']
            self.db = InfluxdbWrapper(conf)
            self.signal = False
            self.old_data = None
            self.old_time = None

        # log format.
        self.enque_log_flag = configuration['sender']['enque_log']
        self.log_format = '\nmeasurement:{}\nunit:{}\ntimestamp:{}\ntags:{}\nfields:{}\n'
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

        if unit == 's':
            date_time = pendulum.from_timestamp(timestamp, tz='Asia/Shanghai').to_datetime_string()
        else:
            date_time = pendulum.from_timestamp(timestamp / 1000000, tz='Asia/Shanghai').to_datetime_string()

        log_str = self.log_format.format(measurement, unit, date_time, tags, fields)
        if self.enque_log_flag:
            log.info(log_str)

        if self.to_where == 'redis':

            # for pack
            tags = msgpack.packb(tags)
            fields = msgpack.packb(fields)
            measurement = msgpack.packb(measurement)
            unit = msgpack.packb(unit)
            timestamp = msgpack.packb(timestamp)

            lua_info = self.db.enqueue(timestamp=timestamp, tags=tags,
                                       fields=fields, measurement=measurement, unit=unit)
            log.info('\n' + lua_info.decode())

        elif self.to_where == 'influxdb':
            if self.threshold(fields, timestamp, unit):
                # influxdb data structure
                josn_data = [
                    {
                        'measurement': measurement,
                        'tags': tags,
                        'time': timestamp,
                        'fields': fields
                    }
                ]

                try:
                    info = self.db.send(josn_data, unit)
                    if info:
                        log.info('send data to inflxudb.{}, {}'.format(josn_data[0]['measurement'], info))
                        if self.signal:
                            self.sqlite_to_influxdb()
                            self.signal = False
                    else:
                        self.sqlite = SqliteWrapper()
                        # When the network is unreachable, store the data in the local sqlite database
                        self.sqlite.enqueue(josn_data, unit)
                        self.signal = True
                except Exception as e:
                    log.error(e)

    def sqlite_to_influxdb(self):
        i = 1
        self.sqlite = SqliteWrapper()
        while True:
            try:
                if self.sqlite.data_len() > 0:
                    results = self.sqlite.dequeue()
                    info = self.db.send(results[1], results[2])
                    log.info('sqlite send data to inflxudb.{}, {}'.format(results[1][0]['measurement'], info))
                    self.sqlite.del_data(results[0])
                else:
                    self.sqlite.drop()
                    break
            except Exception as e:
                log.error(e)
                i += 1
                if i > 10:
                    break

    def threshold(self, fields, timestamp, unit):
        """验证数据是否重复"""
        time_range = 600

        if unit == "s":
            pass
        else:
            time_range *= 1000000

        if self.old_data != fields:
            self.old_data = fields
            self.old_time = timestamp
            return True

        elif self.old_data == fields and timestamp - self.old_time < time_range:
            log.info('ignoring schema worked!')
            return False

        elif self.old_data == fields and timestamp - self.old_time > time_range:
            self.old_time = timestamp
            return True
