# redis_store.py
from flask_redis import FlaskRedis
from .page_data import GenericObject
import os
import pickle


class RedisStoreApp(FlaskRedis):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(RedisStoreApp, cls).__new__(cls, *args, **kwargs)
            cls._instance.files = RedisStoreExecFiles(cls._instance)
        return cls._instance


class FileStat(GenericObject):

    def __init__(self, **kwargs):
        super(FileStat, self).__init__(**kwargs)
        self.status = 'info'
        self.command = 'unknown'
        self.pid = 'unknown'

    def verify(self):
        if not os.path.exists(self.filename):
            self.pid = None
            return False
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            if len(lines) == 0:
                self.pid = 'unkown'
                return False
        return True


# class for the Redis store keeping track of files in the /tmp directory created by the application
class RedisStoreExecFiles:

    def __init__(self, redis_store):
        self.redis_store = redis_store

    def get_files(self):
        return self.redis_store.hkeys('files')

    def get_files_dict(self):
        _files = []
        for k in self.redis_store.hkeys('files'):
            _file = self.get_file(k.decode())
            if _file is not None:
                if _file.verify():
                    # fdict = {'filename': _file.filename, 'status': _file.status, 'command': _file.command}
                    fdict = {'filename': 'test', 'status': 'test', 'command': 'test'}
                    _files.append(fdict)
                else:
                    self.remove_file(k.decode())
            else:
                self.remove_file(k.decode())
        return _files

    def add_file(self, filename, pid=None):
        _file = FileStat(filename=filename, pid=pid)
        if _file.verify():
            _file_pickled = pickle.dumps(_file)
            self.redis_store.hset('files', filename, _file_pickled)
        else:
            self.remove_file(filename)

    def get_file(self, filename):
        _file_pickled = self.redis_store.hget('files', filename)
        if _file_pickled is not None:
            _file = pickle.loads(_file_pickled)
            return _file
        return None

    def remove_file(self, filename):
        self.redis_store.hdel('files', filename)
