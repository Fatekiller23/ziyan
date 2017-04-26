# --*-- coding=utf-8 --*--
"""
包装各种数据库模块, 使其易于使用
"""
import time
import traceback

import redis
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from logbook import Logger
from redis.exceptions import ConnectionError
from requests.exceptions import ConnectionError as Connectionerror

log = Logger('database_wrapper')

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
        self.__db = redis.Redis(connection_pool=pool)

        # 测试redis连通性
        self.__connect()

    def __connect(self):
        """
        初始化连接 Redis 数据库, 确保 redis 连接成功 
        :return: None
        """
        while True:
            try:
                self.__db.ping()
                break
            except ConnectionError:
                log.error(traceback.print_exc())
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
            self.sha = self.__db.script_load(script)

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
        return self.__db.evalsha(self.sha, 1, tags, timestamp, fields, measurement)

    def dequeue(self, key):
        """
        Remove and return the first item of the list ``data_queue``
        if ``data_queue`` is an empty list, block indefinitely
        """
        return self.__db.blpop(key)

    def get_len(self, key):
        """
        Return the length of the list ``data_queue``
        """
        return self.__db.llen(key)

    def queue_back(self, key, data):
        """
        Push the data onto the head of the list ``data_queue``
        """
        return self.__db.lpush(key, data)

    def flushdb(self):
        """
        Delete all keys in the current database
        """
        return self.__db.flushdb()

    def keys(self, pattern='*'):
        """
        Returns a list of keys matching ``pattern``
        """
        return self.__db.keys(pattern)


class InfluxdbWrapper:
    """
    包装 influxdb 库
    
    用法：
    josn_data = [
        {
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "time": "2009-11-10T23:00:00Z",
            "fields": {
                "value": 0.64
            }
        }
    ]
    db = InfluxdbWrapper('localhost', 8086, 'root', 'root', db) or InfluxdbWrapper(conf)
    db.send(josn_data, retention_policy='specify')
    """
    def __init__(self, *args, **kwargs):
        if args and len(args) == 5:
            self.__db = InfluxDBClient(
                host=args[0],
                port=args[1],
                username=args[2],
                password=args[3],
                database=args[4],
                timeout=1
            )
        elif kwargs:
            self.__db = InfluxDBClient(
                host=kwargs.get('host', 'localhost'),
                port=kwargs.get('port', 8086),
                username=kwargs['username'],
                password=kwargs['password'],
                database=kwargs['db'],
                timeout=kwargs.get('timeout', 1)
            )
        else:
            log.error('No influxdb address')
        self.conf = kwargs

        #测试 influxdb 连通性
        self.__connect()

    def __connect(self):
        """
        初始化连接 Influxdb 数据库, 确保 Influxdb 连接成功 
        :return: None
        """
        while True:
            try:
                self.__db.get_list_database()
                break
            except (Connectionerror, InfluxDBClientError):
                log.error(traceback.print_exc())
                time.sleep(2)
                continue

    def send(self, json_body, database=None, retention_policy=None):
        """
        Write to multiple time series names
        :param json_body:  list of dictionaries, each dictionary represents a point, 
                            the list of points to be written in the database
        :param database: str,  the database to write the points to. Defaults to the client’s current database
        :param retention_policy: str, the retention policy for the points. Defaults to None
        :return: bool
        """
        return self.__db.write_points(json_body, time_precision=self.conf.get('time_precision', 's')
                                    , database=database, retention_policy=retention_policy)

    def swith_database(self, database):
        """
        Change the client’s database.
        :param database: str, database name
        :return: None
        """
        self.__db.switch_database(database)
