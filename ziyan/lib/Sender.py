# -*- coding: utf-8 -*-

class Sender:
    """
    用不同的databas wrapper，将数据以相应格式发送的sender
    """

    def __init__(self, to_where):
        self.to_where = to_where
        pass

    def receive(self, data):
        """
        
        :param data: format {'fields': {'Msg': '我是check的data'}, 
                            'timestamp': 1492572292, 'tags': {'eqpt_no': 'pec0-001', 'source': 's1'}, 
                            'measurement': 'test_measurement'}
        :return: None
        """
        pass

    def send(self):
        """
        将队列里打包好的数据发送出去
        :return: 
        """
        pass

    def pack(self):
        """
        以发送的目标规定格式打包好数据
        
        :return: 
        """
        pass
