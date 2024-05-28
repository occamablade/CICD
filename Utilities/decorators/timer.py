from time import time, strftime, gmtime
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def execution_time(_func):
    @wraps(_func)
    def _timer(*args, **kwargs):
        start = time()
        f = _func(*args, **kwargs)
        elapsed = time() - start
        logger.info(
            'Работа функции [ {} ] длилась: [ {} ]'.format(_func.__name__, strftime("%H:%M:%S", gmtime(elapsed))))
        return f

    return _timer


class MetaExecutionTimeDecorator(type):

    def __new__(mcs, name, bases, attrs):
        for method_name, method_object in attrs.items():
            if callable(method_object):
                attrs[method_name] = mcs.timer(method_object, method_name)
        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def timer(method, method_name):
        def wrapper(*args, **kwargs):
            start = time()
            func = method(*args, **kwargs)
            elapsed = time() - start
            logger.info(
                'Время работы функции {} составляет {}'.format(method_name, strftime("%H:%M:%S", gmtime(elapsed))))
            return func

        return wrapper


class ValidationArgType(type):

    def __new__(cls, name, bases, attrs):
        for method_name, method_object in attrs.items():
            if callable(method_object):
                attrs[method_name] = cls.validation(method_object)
        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def validation(method):
        def _wrapper(*args, **kwargs):
            for arg in args[1::]:
                if not isinstance(arg, str):
                    raise ValueError(f'Все аргументы должны быть строками. Неверный тип аргумента [ {arg} ]')
            for k, val in kwargs.items():
                if not isinstance(val, str):
                    raise ValueError(f'Все аргументы должны быть строками. Неверный тип аргумента [ {k} ]')
            return method(*args, **kwargs)

        return _wrapper
