# --*-- coding=utf-8 --*--
"""

"""
import time
import traceback

import redis


class Redis_wrapper:
    def __init__(self, conf):
        pool = redis.ConnectionPool(
            host=conf['host'],
            port=conf['port'],
            db=conf['db'])
        self.db = redis.Redis(connection_pool=pool)
        self.connect()

    def connect(self):
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
        with open(lua_script_file, 'r') as fn:
            script = fn.read()
            self.sha = self.db.script_load(script)

    def enqueue(self, **kwargs):
        self.db.evalsha(self.sha, 1, kwargs)

    def dequeue(self):
        return self.db.blpop("data_queue")

    def get_len(self):
        return self.db.llen("data_queue")

    def queue_back(self, data):
        return self.db.lpush('data_queue', data)
