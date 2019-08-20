#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-12-26 下午3:32
"""
import atexit
import multiprocessing
import secrets
import string
import sys
from collections import MutableMapping, MutableSequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

import aelog
import redis
import yaml
from bson import ObjectId
from flask import Flask
from redis.exceptions import RedisError

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

__all__ = ("ignore_error", "verify_message", "analysis_yaml", "gen_class_name", "objectid", "gen_ident",
           "thread_pool", "pool_submit", "apscheduler_start")

# 执行任务的线程池
thread_pool = ThreadPoolExecutor(multiprocessing.cpu_count() * 10 + multiprocessing.cpu_count())


def apscheduler_start(app_: Flask, scheduler):
    """
    apscheduler的启动方法，利用redis解决多进程多实例的问题
    Args:
        app_: app应用实例
        scheduler: apscheduler的调度实例
    Returns:

    """
    try:
        from flask_apscheduler import APScheduler
        if not isinstance(scheduler, APScheduler):
            raise ValueError("scheduler类型错误")
    except ImportError as e:
        raise ImportError(e)

    rdb = None
    try:
        rdb = redis.StrictRedis(
            host=app_.config["ECLIENTS_REDIS_HOST"], port=app_.config["ECLIENTS_REDIS_PORT"],
            db=2, password=app_.config["ECLIENTS_REDIS_PASSWD"], decode_responses=True)
    except RedisError as e:
        aelog.exception(e)
    else:
        if rdb.get("apscheduler") is None:
            rdb.set("apscheduler", "apscheduler")
            scheduler.start()
    finally:
        if rdb:
            rdb.connection_pool.disconnect()

    @atexit.register
    def remove_apscheduler():
        """
        移除redis中保存的标记
        Args:

        Returns:

        """
        rdb_ = None
        try:
            rdb_ = redis.StrictRedis(
                host=app_.config["ECLIENTS_REDIS_HOST"], port=app_.config["ECLIENTS_REDIS_PORT"],
                db=2, password=app_.config["ECLIENTS_REDIS_PASSWD"], decode_responses=True)
        except RedisError as ex:
            aelog.exception(ex)
        else:
            rdb_.delete("apscheduler")
        finally:
            if rdb_:
                rdb_.connection_pool.disconnect()


def pool_submit(func, *args, task_name="", **kwargs):
    """
    执行长时间任务的线程调度方法
    Args:
        func, *args, **kwargs
    Returns:

    """

    def callback_done(fn):
        """
        线程回调函数
        Args:

        Returns:

        """
        try:
            data = fn.result()
        except Exception as e:
            aelog.exception("error,{} return result: {}".format(task_name, e))
        else:
            aelog.info("{} return result: {}".format(task_name, data))

    future_result = thread_pool.submit(func, *args, **kwargs)
    future_result.add_done_callback(callback_done)


def gen_ident(ident_len=8):
    """
    获取随机的标识码以字母开头， 默认8个字符的长度
    Args:

    Returns:

    """
    ident_len = ident_len - 1
    alphabet = f"{string.ascii_lowercase}{string.digits}"
    ident = ''.join(secrets.choice(alphabet) for _ in range(ident_len))
    return f"{secrets.choice(string.ascii_lowercase)}{ident}"


@contextmanager
def ignore_error(error=Exception):
    """
    个别情况下会忽略遇到的错误
    Args:

    Returns:

    """
    # noinspection PyBroadException
    try:
        yield
    except error:
        pass


def verify_message(src_message: dict, message: list or dict):
    """
    对用户提供的message进行校验
    Args:
        src_message: 默认提供的消息内容
        message: 指定的消息内容
    Returns:

    """
    src_message = dict(src_message)
    message = message if isinstance(message, MutableSequence) else [message]
    required_field = {"msg_code", "msg_zh", "msg_en"}

    for msg in message:
        if isinstance(msg, MutableMapping):
            if set(msg.keys()).intersection(required_field) == required_field and msg["msg_code"] in src_message:
                src_message[msg["msg_code"]].update(msg)
    return src_message


def gen_class_name(underline_name):
    """
    由下划线的名称变为驼峰的名称
    Args:
        underline_name
    Returns:

    """
    return "".join(name.capitalize() for name in underline_name.split("_"))


def analysis_yaml(full_conf_path):
    """
    解析yaml文件
    Args:
        full_conf_path: yaml配置文件路径
    Returns:

    """
    with open(full_conf_path, 'rt', encoding="utf8") as f:
        try:
            conf = yaml.load(f, Loader=Loader)
        except yaml.YAMLError as e:
            print("Yaml配置文件出错, {}".format(e))
            sys.exit()
    return conf


def objectid():
    """

    Args:

    Returns:

    """
    return str(ObjectId())
