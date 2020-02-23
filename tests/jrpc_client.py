#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 2020/2/21 下午2:14
"""
from eclients import HttpClient
from eclients.jsonrpc import JRPCClient


def sub(client: JRPCClient):
    """

    Args:

    Returns:

    """
    r = client["local"].sub(5, 2).done()
    print(r)
    s = client["local"].test().done()
    print(s)

    s2 = client["local"].sub(5, 2).test(3).done()
    print(s2)
    s3 = client["local"].sub(5, 2).test().echo_mystr(5, 6).echo_mystr(sss=55, ssd=66).done()
    print(s3)


if __name__ == '__main__':
    aio_http = HttpClient()
    aio_http.init_session()
    aio_jrpc = JRPCClient(aio_http)
    aio_jrpc.register("local", ("127.0.0.1", 8000))
    aio_jrpc.register("loca2", ("127.0.0.1", 8001))
    sub(aio_jrpc)
