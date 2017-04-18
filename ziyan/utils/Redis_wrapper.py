# --*-- coding=utf-8 --*--
"""
包装 redis 库, 用 lua 脚本作为入队筛选机制

用法：
db = Redis_wrapper.RedisWrapper(conf)
db.script_load(lua_file)
db.enqueue(**kwargs)  #入队
"""
import time
import traceback
import redis


class RedisWrapper:
    def __init__(self, conf):
        """
        :param conf: dict, 包含 Redis 的 host, port, db
        """
        pool = redis.ConnectionPool(
            host=conf['host'],
            port=conf['port'],
            db=conf['db'])
        self.db = redis.Redis(connection_pool=pool)
        self.connect()

    def connect(self):
        """
        初始化连接 Redis 数据库, 确保 redis 连接成功 
        :return: None
        """
        while True:
            try:
                a = self.db.keys()
                del a
                break
            except Exception as e:
                traceback.print_exc()
                time.sleep(2)
                continue

    def script_load(self, lua_script_file):
        """
        加载 Lua 脚本, 生成对应的 sha, 保存在类属性中
        :param lua_script_file: Lua file path
        :return: None
        """
        with open(lua_script_file, 'r') as fn:
            script = fn.read()
            self.sha = self.db.script_load(script)

    def enqueue(self, **kwargs):
        """
        将传入的 dict 传入 Lua 脚本进行处理，默认第一个值为 key
        :param kwargs: dict
        :return: lua 脚本返回值
        """
        eqpt_no = kwargs.pop('eqpt_no')
        timestamp = kwargs.pop('timestamp')
        data = kwargs.pop('data')
        measurement = kwargs.pop('measurment')
        return self.db.evalsha(self.sha, 1, eqpt_no, timestamp, data, measurement)

    def dequeue(self):
        """
        Remove and return the first item of the list ``data_queue``
        if ``data_queue`` is an empty list, block indefinitely
        """
        return self.db.blpop("data_queue")

    def get_len(self):
        """
        Return the length of the list ``data_queue``
        """
        return self.db.llen("data_queue")

    def queue_back(self, data):
        """
        Push the data onto the head of the list ``data_queue``
        """
        return self.db.lpush('data_queue', data)
