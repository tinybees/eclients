#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 19-1-21 下午6:47
"""
import weakref
from functools import wraps
from typing import Dict, Union

import aelog
from flask import g, request
from marshmallow import EXCLUDE, Schema, ValidationError

from .err_msg import schema_msg
from .exceptions import FuncArgsError, HttpError
from .utils import verify_message

__all__ = ("singleton", "schema_validate", "Singleton", "Cached")


def singleton(cls):
    """
    singleton for class
    """

    instances = {}

    @wraps(cls)
    def _singleton(*args, **kwargs):
        """
        singleton for class of app
        """
        cls_name = "_{0}".format(cls)
        if cls_name not in instances:
            instances[cls_name] = cls(*args, **kwargs)
        return instances[cls_name]

    return _singleton


class _Singleton(type):
    """
    singleton for class
    """

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
            return cls.__instance
        else:
            return cls.__instance


class _Cached(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__cache = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        cached_name = f"{args}{kwargs}"
        if cached_name in cls.__cache:
            return cls.__cache[cached_name]
        else:
            obj = super().__call__(*args, **kwargs)
            cls.__cache[cached_name] = obj  # 这里是弱引用不能直接赋值，否则会被垃圾回收期回收
            return obj


class Singleton(metaclass=_Singleton):
    pass


class Cached(metaclass=_Cached):
    pass


def schema_validate(schema_obj, required: Union[tuple, list] = tuple(), is_extends: bool = True,
                    excluded: Union[tuple, list] = tuple(), use_zh: bool = True, message: Dict = None):
    """
    校验post的json格式和类型是否正确
    Args:
        schema_obj: 定义的schema对象
        required: 需要标记require的字段
        excluded: 排除不需要的字段
        is_extends: 是否继承schemea本身其他字段的require属性， 默认继承
        use_zh: 消息提示是否使用中文，默认中文
        message: 提示消息
    Returns:
    """

    if not issubclass(schema_obj, Schema):
        raise FuncArgsError(message="schema_obj type error!")
    if not isinstance(required, (tuple, list)):
        raise FuncArgsError(message="required type error!")
    if not isinstance(excluded, (tuple, list)):
        raise FuncArgsError(message="excluded type error!")

    msg_zh = "msg_zh" if use_zh else "msg_en"
    # 此处的功能保证，如果调用了多个校验装饰器，则其中一个更改了，所有的都会更改
    if not getattr(schema_validate, "message", None):
        setattr(schema_validate, "message", verify_message(schema_msg, message or {}))

    def _validated(func):
        """
        校验post的json格式和类型是否正确
        """

        @wraps(func)
        def _wrapper(*args, **kwargs):
            """
            校验post的json格式和类型是否正确
            """
            schema_message = getattr(schema_validate, "message", None)

            new_schema_obj = schema_obj(unknown=EXCLUDE)
            if required:
                for key, val in new_schema_obj.fields.items():
                    if key in required:  # 反序列化期间，把特别需要的字段标记为required
                        setattr(new_schema_obj.fields[key], "required", True)
                        setattr(new_schema_obj.fields[key], "dump_only", False)
                    elif not is_extends:
                        setattr(new_schema_obj.fields[key], "required", False)
            try:
                valid_data = new_schema_obj.load(request.json, unknown=EXCLUDE)
                # 把load后不需要的字段过滤掉，主要用于不允许修改的字段load后过滤掉
                for val in excluded:
                    valid_data.pop(val, None)
            except ValidationError as err:
                # 异常退出
                aelog.exception('Request body validation error, please check! {} {} error={}'.format(
                    request.method, request.path, err.messages))
                raise HttpError(400, message=schema_message[201][msg_zh], error=err.messages)
            except Exception as err:
                aelog.exception("Request body validation unknow error, please check!. {} {} error={}".format(
                    request.method, request.path, str(err)))
                raise HttpError(500, message=schema_message[202][msg_zh], error=str(err))
            else:
                g.json = valid_data
            return func(*args, **kwargs)

        return _wrapper

    return _validated
