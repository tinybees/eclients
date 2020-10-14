#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-12-26 下午3:32
"""
import atexit
import multiprocessing
import os
import secrets
import string
import sys
from collections import MutableMapping, MutableSequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Callable, Dict, List, NoReturn, Union

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
           "thread_pool", "pool_submit", "apscheduler_start", "number", "apscheduler_warkup_job")

# 执行任务的线程池
thread_pool = ThreadPoolExecutor(multiprocessing.cpu_count() * 10 + multiprocessing.cpu_count())


# noinspection PyProtectedMember
def apscheduler_warkup_job(scheduler):
    """
    唤醒job
    Args:

    Returns:

    """
    scheduler._scheduler.wakeup()


# noinspection PyProtectedMember
def apscheduler_start(app_: Flask, scheduler, is_warkup: bool = True, warkup_func: Callable = None,
                      warkup_seconds: int = 3600) -> NoReturn:
    """
    apscheduler的启动方法，利用redis解决多进程多实例的问题

    warkup_func可以包装apscheduler_warkup_job即可
    def warkup_func():
        apscheduler_warkup_job(scheduler)  # 这里的scheduler就是启动后的apscheduler全局实例
    Args:
        app_: app应用实例
        scheduler: apscheduler的调度实例
        is_warkup: 是否定期发现job，用于非运行scheduler进程添加的job
        warkup_func: 唤醒的job函数，可以包装apscheduler_warkup_job
        warkup_seconds: 定期唤醒的时间间隔
    Returns:

    """

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
        except RedisError as err:
            aelog.exception(err)
        else:
            with ignore_error():
                rdb_.delete("apscheduler")
                aelog.info(f"当前进程{os.getpid()}清除redis[2]任务标记[apscheduler].")
        finally:
            if rdb_:
                rdb_.connection_pool.disconnect()

    try:
        from flask_apscheduler import APScheduler
        if not isinstance(scheduler, APScheduler):
            raise ValueError("scheduler类型错误")
    except ImportError as e:
        raise ImportError(f"please install flask_apscheduler {e}")

    rdb = None
    try:
        rdb = redis.StrictRedis(
            host=app_.config["ECLIENTS_REDIS_HOST"], port=app_.config["ECLIENTS_REDIS_PORT"],
            db=2, password=app_.config["ECLIENTS_REDIS_PASSWD"], decode_responses=True)
    except RedisError as e:
        aelog.exception(e)
    else:
        with rdb.lock("apscheduler_lock"):
            if rdb.get("apscheduler") is None:
                rdb.set("apscheduler", "apscheduler")
                scheduler.start()
                if is_warkup and callable(warkup_func):
                    scheduler.add_job("warkup", warkup_func, trigger="interval", seconds=warkup_seconds,
                                      replace_existing=True)
                atexit.register(remove_apscheduler)
                aelog.info(f"当前进程{os.getpid()}启动定时任务成功,设置redis[2]任务标记[apscheduler],"
                           f"任务函数为{warkup_func.__name__}.")
            else:
                scheduler._scheduler.state = 2
                aelog.info(f"其他进程已经启动了定时任务,当前进程{os.getpid()}不再加载定时任务.")
    finally:
        if rdb:
            rdb.connection_pool.disconnect()


def pool_submit(func: Callable, *args, task_name: str = "", **kwargs):
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


def gen_ident(ident_len: int = 8):
    """
    获取随机的标识码以字母开头， 默认8个字符的长度
    Args:

    Returns:

    """
    alphabet = f"{string.ascii_lowercase}{string.digits}"
    ident = ''.join(secrets.choice(alphabet) for _ in range(ident_len - 1))
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


def verify_message(src_message: Dict, message: Union[List, Dict]) -> Union[List, Dict]:
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


def gen_class_name(underline_name: str) -> str:
    """
    由下划线的名称变为驼峰的名称
    Args:
        underline_name
    Returns:

    """
    return "".join(name.capitalize() for name in underline_name.split("_"))


def analysis_yaml(full_conf_path: str) -> Dict:
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


def objectid() -> str:
    """

    Args:

    Returns:

    """
    return str(ObjectId())


def number(str_value: str, default: int = 0) -> Union[int, float]:
    """
    把字符串值转换为int或者float
    Args:
        str_value: 需要转换的字符串值
        default: 转换失败的默认值,默认值只能为Number类型,默认为0
    Returns:

    """
    default = default if isinstance(default, (int, float)) else 0
    if isinstance(str_value, str):
        number_value = default  # 先赋予默认值
        # 处理有符号的整数和小数
        if str_value.startswith(("-", "+")):
            if str_value[1:].isdecimal():
                number_value = int(str_value)
            elif str_value[1:].replace(".", "").isdecimal():
                number_value = float(str_value)
        # 处理无符号的整数
        elif str_value.isdecimal():
            number_value = int(str_value)
        # 处理无符号的小数
        elif str_value.replace(".", "").isdecimal():
            number_value = float(str_value)

        return number_value
    elif isinstance(str_value, (int, float)):
        return str_value
    else:
        return default
