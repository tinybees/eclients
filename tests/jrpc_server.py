#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 2020/2/21 下午1:47
"""
from flask import Flask

from eclients.jsonrpc import FlaskJsonRPC

app = Flask(__name__)
jsonrpc = FlaskJsonRPC(app)


@jsonrpc.method('fails')
def fails(ddd):
    raise IndexError


@jsonrpc.method('echo_mystr')
def echo_mystr(sss=None, ssd=None):
    return sss, ssd


@jsonrpc.method("sub")
def sub(a: int, b: int) -> int:
    return a - b


@jsonrpc.method("test")
def test() -> str:
    return "中文"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
