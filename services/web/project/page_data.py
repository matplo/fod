# page_data.py
import json


class GenericObject(object):
    max_chars = 1000

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
        if self.args:
            self.configure_from_dict(self.args.__dict__)
        if self.init_dict:
            self.configure_from_dict(self.init_dict)
        if self.init_json:
            self.configure_from_json(self.init_json)

    def configure_from_args(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def configure_from_dict(self, d, ignore_none=False):
        for k in d:
            if ignore_none and d[k] is None:
                continue
            self.__setattr__(k, d[k])

    def configure_from_json(self, js, ignore_none=False):
        d = json.loads(js)
        for k in d:
            if ignore_none and d[k] is None:
                continue
            self.__setattr__(k, d[k])

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            pass
        self.__setattr__(key, None)
        return self.__getattr__(key)

    def __str__(self) -> str:
        s = []
        s.append('[i] {} ({})'.format(str(self.__class__).split('.')[1].split('\'')[0], id(self)))
        for a in self.__dict__:
            if a[0] == '_':
                continue
            sval = str(getattr(self, a))
            if len(sval) > self.max_chars:
                sval = sval[:self.max_chars - 4] + '...'
            s.append('   {} = {}'.format(str(a), sval))
        return '\n'.join(s)

    def __repr__(self) -> str:
        return self.__str__()

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __iter__(self):
        _props = [a for a in self.__dict__ if a[0] != '_']
        return iter(_props)


class PageData(GenericObject):

    def __init__(self, **kwargs):
        super(PageData, self).__init__(**kwargs)
