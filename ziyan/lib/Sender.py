# -*- coding: utf-8 -*-
import msgpack


class Sender:
    """
    用不同的databas wrapper，将数据以相应格式发送的sender
    """

    def __init__(self, configuration):
        self.to_where = configuration['sender']['send_to_where']
        if self.to_where == 'redis':
            from ziyan.utils.database_wrapper import RedisWrapper
            # Fixme 目前暂时调试 以后调试需要更改
            conf = {'host': 'localhost', 'port': 6379, 'db': 1}
            self.redis = RedisWrapper(conf)

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
        timestamp = data.pop('timestamp')
        tags = msgpack.packb(data.pop('tags'))
        fields = msgpack.packb(data.pop('fields'))
        measurement = msgpack.packb(data.pop('measurement'))

        if self.to_where == 'redis':
            self.redis.script_load(r'ziyan\text_file\enque_script.lua')
            print(self.redis.enqueue(timestamp=timestamp, tags=tags,
                                     fields=fields, measurement=measurement))
