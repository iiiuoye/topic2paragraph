import logging
import sys
import traceback
import random
import time
import io
import os
from dateutil import parser


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton

@Singleton
class Logger(logging.Logger):
    def __init__(self, application: str='webface'):
        super().__init__(application, logging.INFO)
        fmt = '%(asctime)s %(levelname)s: %(message)s'
        hdlr = logging.StreamHandler(sys.stdout)
        hdlr.formatter = logging.Formatter(fmt)
        self.addHandler(hdlr)
        path = os.path.join(os.path.split(get_root_path())[0], 'logs')
        if not os.path.exists(path):
            os.makedirs(path)
        hdlr = logging.FileHandler(os.path.join(path, '{}.log'.format(time.time())))
        hdlr.formatter = logging.Formatter(fmt)
        self.addHandler(hdlr)


def exception_handler(func):
    def wrapper(*args, **kwargs):
        result = {'code': 1201999, 'data': None, 'error': 'inner error'}
        try:
            result = func(*args, **kwargs)
        except:
            error = traceback.format_exc()
            Logger().error(error)
            result['data'] = error
        finally:
            return result
            
    wrapper.__name__ = func.__name__
    return wrapper

def sleep(lower, upper):
    time.sleep(random.uniform(lower, upper))

def get_root_path():
    return os.path.split(os.path.realpath(__file__))[0]

def time_parse(timestr):
    return parser.parse(timestr)