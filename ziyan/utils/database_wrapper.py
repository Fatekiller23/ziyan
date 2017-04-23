# --*-- coding=utf-8 --*--
"""
包装各种数据库模块, 使其易于使用
"""
import time
import traceback

import redis
from redis.exceptions import ConnectionError
from influxdb import InfluxDBClient


class RedisWrapper:
    """
    包装 redis 库, 用 lua 脚本作为入队筛选机制

    用法：
    db = database_wrapper.RedisWrapper(conf)
    db.script_load(lua_file)
    db.enqueue(**kwargs)  #入队
    """

    def __init__(self, conf):
        """
        :param conf: dict, 包含 Redis 的 host, port, db
        """
        pool = redis.ConnectionPool(
            host=conf.get('host', 'localhost'),
            port=conf.get('port', 6379),
            db=conf.get('db', 0))
        self.db = redis.Redis(connection_pool=pool)

        # 测试redis连通性
        self.connect()

    def connect(self):
        """
        初始化连接 Redis 数据库, 确保 redis 连接成功 
        :return: None
        """
        while True:
            try:
                self.db.ping()
            except ConnectionError:
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
        将传入的参数传入 Lua 脚本进行处理，默认第一个值为 key
        :param kwargs: 位置参数
        :return: lua 脚本返回值
        """
        timestamp = kwargs.pop('timestamp')
        tags = kwargs.pop('tags')
        fields = kwargs.pop('fields')
        measurement = kwargs.pop('measurement')
        return self.db.evalsha(self.sha, 1, tags, timestamp, fields, measurement)

    def dequeue(self, key):
        """
        Remove and return the first item of the list ``data_queue``
        if ``data_queue`` is an empty list, block indefinitely
        """
        return self.db.blpop(key)

    def get_len(self, key):
        """
        Return the length of the list ``data_queue``
        """
        return self.db.llen(key)

    def queue_back(self, key, data):
        """
        Push the data onto the head of the list ``data_queue``
        """
        return self.db.lpush(key, data)

    def flushdb(self):
        """
        Delete all keys in the current database
        """
        return self.db.flushdb()

    def keys(self, pattern='*'):
        """
        Returns a list of keys matching ``pattern``
        """
        return self.db.keys(pattern)


class InfluxdbWrapper:
    def __init__(self, conf):
        self.db = InfluxDBClient(
            host=conf.get('host', 'local'),
            port=conf.get('port', 8086),
            username=conf['username'],
            password=conf['password'],
            database=conf['db'])
