# redis_store.py
from flask_redis import FlaskRedis
from .page_data import GenericObject
import os
import json
import logging
logger = logging.getLogger('project')


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
        if self.status is None:
            self.status = 'info'
        if self.command is None:
            self.command = 'unknown'
        if self.pid is None:
            self.pid = 'unknown'
        self.verify()

    def as_dict(self):
        return {'filename': self.filename, 'status': self.status, 'command': self.command, 'pid': self.pid}

    def as_json(self):
        return json.dumps(self.as_dict())

    def verify(self):
        if not os.path.exists(self.filename):
            self.pid = None
            return False
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            if len(lines) == 0:
                self.pid = 'unkown'
                return False
            self.command = lines[0].split('#begin [')[1].split(']')[0]
            # if lines[-1].startswith(f'#end [{self.command}]'):
            if lines[-1].startswith('#end ') and lines[-1].endswith(f'{self.filename}\n'):
                self.status = 'success'
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
                    _files.append(_file.as_dict())
        return _files

    def add_file(self, filename, pid=None):
        _file = FileStat(filename=filename, pid=pid)
        if _file.verify():            
            self.redis_store.hset('files', filename, _file.as_json())
            self.get_file(filename)

    def get_file(self, filename):
        _file_json = self.redis_store.hget('files', filename).decode()
        if _file_json is not None:
            _file = FileStat(init_json=_file_json)            
            return _file
        return None

    def remove_file(self, filename):
        self.redis_store.hdel('files', filename)
