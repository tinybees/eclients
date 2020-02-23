#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 2020/2/21 下午5:00
"""
from inspect import getfullargspec
from typing import Optional

from flask import Flask

try:
    # noinspection PyProtectedMember
    from flask_jsonrpc import JSONRPC, default_site, authenticate, _inject_args, _parse_sig
except ImportError as e:
    raise e

__all__ = ("FlaskJsonRPC",)


class FlaskJsonRPC(JSONRPC):
    """

    """

    def __init__(self, app: Flask, auth_backend=authenticate, site=default_site,
                 enable_web_browsable_api=False):
        """

        Args:

        """
        service_url: Optional[str] = "/api/jrpc/post"
        # ws_route: Optional[str] = "/api/jrpc/ws"
        super().__init__(app, service_url=service_url, auth_backend=auth_backend, site=site,
                         enable_web_browsable_api=enable_web_browsable_api)

    def method(self, name, authenticated=False, safe=False, validate=False, **options):
        def decorator(f):
            arg_names = getfullargspec(f)[0]
            name_args = {'name': name, 'arg_names': arg_names}
            if authenticated:
                name_args['arg_names'] = ['username', 'password'] + name_args['arg_names']
                name_args['name'] = _inject_args(name_args['name'], ('String', 'String'))
                _f = self.auth_backend(f, authenticated)
            else:
                _f = f
            method, arg_types, return_type = _parse_sig(name_args['name'], name_args['arg_names'], validate)
            _f.json_args = name_args['arg_names']
            _f.json_arg_types = arg_types
            _f.json_return_type = return_type
            _f.json_method = method
            _f.json_safe = safe
            _f.json_sig = name_args['name']
            _f.json_validate = validate
            self.site.register(method, _f)
            return _f

        return decorator
