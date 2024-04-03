# redis_store.py
from flask_redis import FlaskRedis


class RedisStoreApp(FlaskRedis):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(RedisStoreApp, cls).__new__(cls, *args, **kwargs)
            cls._instance.files = RedisStoreExecFiles(cls._instance)
        return cls._instance


# class for the Redis store keeping track of files in the /tmp directory created by the application
class RedisStoreExecFiles:

    def __init__(self, redis_store):
        self.redis_store = redis_store

    def get_files(self):
        return self.redis_store.keys()

    def get_files_str(self):
        return [k.decode() for k in self.redis_store.keys()]

    def add_file(self, filename):
        self.redis_store.set(filename, "1")

    def remove_file(self, filename):
        self.redis_store.delete(filename)
