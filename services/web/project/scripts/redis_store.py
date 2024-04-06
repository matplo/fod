# redis_store.py
from flask_redis import FlaskRedis
from .page_data import GenericObject
import os
import json
import time
import re
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
            self.status = 'link'
        if self.command is None:
            self.command = 'unknown'
        if self.pid is None:
            self.pid = 'unknown'
        self.verify()

    def as_dict(self):
        return {'filename': self.filename, 'status': self.status, 'command': self.command, 'pid': self.pid}

    def as_json(self):
        return json.dumps(self.as_dict())

    def _get_cmnd_and_ctime(self, line):
        # Regular expression pattern
        pattern = r'\[(.*?)\]'
        # Find all matches of the pattern
        matches = re.findall(pattern, line)
        if len(matches) == 0:
            return None, 0
        if len(matches) == 1:
            return matches[0], 0
        if len(matches) > 1:
            return matches[0], float(matches[1])

    def verify(self):
        if not os.path.exists(self.filename):
            self.pid = None
            self.status = 'danger'
            return False
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            if len(lines) == 0:
                self.status = 'danger'
                return False
            # self.command = lines[0].split('#begin [')[1].split(']')[0]
            self.command, self.ctime = self._get_cmnd_and_ctime(lines[0])
            self.cctime = time.ctime(self.ctime)
            # if lines[-1].startswith(f'#end [{self.command}]'):
            if lines[-1].startswith('#end ') and lines[-1].endswith(f'{self.filename}\n'):
                self.status = 'success'
            if len([True for _l in lines if _l.startswith('#ERROR_FLAG -')]):
                self.status = 'danger'
        self.mtime = os.path.getmtime(self.filename)
        self.cmtime = time.ctime(self.mtime)
        return True


# class for the Redis store keeping track of files in the /tmp directory created by the application
class RedisStoreExecFiles:

    def __init__(self, redis_store):
        self.redis_store = redis_store

    def get_files(self):
        return self.redis_store.hkeys('files')

    def get_files_dict_slow(self):
        _files = []
        for k in self.redis_store.hkeys('files'):
            _file = self.get_file(k.decode())
            if _file is not None:
                if _file.verify():
                    _files.append(_file.as_dict())
        return _files

    def get_files_dict(self):
        _dict = self.redis_store.hgetall('files')
        _files = []
        for k in _dict:
            _file = _dict[k].decode()
            if _file is not None:
                if _file.verify():
                    _files.append(_file.as_dict())
        return _files

    def get_files_list(self):
        _files = []
        for k in self.redis_store.hkeys('files'):
            _file = self.get_file(k.decode())
            if _file is not None:
                if _file.verify():
                    # _files.append(_file.as_dict())
                    _files.append(_file)
        _files.sort(key=lambda x: x.mtime, reverse=True)
        return _files

    def add_file(self, filename, pid=None):
        _file = FileStat(filename=filename, pid=pid)
        if _file.verify():
            self.redis_store.hset('files', filename, _file.as_json())
        return self.get_file(filename)

    def get_file(self, filename):
        _file_json = self.redis_store.hget('files', filename).decode()
        if _file_json is not None:
            _file = FileStat(init_json=_file_json)
            return _file
        return None

    def remove_file(self, filename):
        self.redis_store.hdel('files', filename)
