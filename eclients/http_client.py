#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-7-1 上午10:08
"""
import atexit
from typing import Dict

import requests as sync_requests
from requests.exceptions import ConnectTimeout, ConnectionError, HTTPError, RequestException, Timeout

from eclients.err_msg import http_msg
from eclients.utils import verify_message
from .decorators import Singleton
from .exceptions import ClientConnectionError, ClientError, ClientResponseError

__all__ = ("HttpClient", "Response")


class Response(object):
    """
    响应对象,需要重新封装对象
    """
    __slots__ = ["status_code", "reason", "headers", "cookies", "resp_body", "content"]

    def __init__(self, status_code: int, reason: str, headers: Dict, cookies: Dict, *, resp_body: Dict,
                 content: bytes):
        """

        Args:

        """
        self.status_code = status_code
        self.reason = reason
        self.headers = headers
        self.cookies = cookies
        self.resp_body = resp_body
        self.content = content

    def json(self, ):
        """
        为了适配
        Args:

        Returns:

        """
        return self.resp_body


class HttpClient(Singleton):
    """
    基于requests的同步封装
    """

    def __init__(self, app=None, *, timeout: int = 5 * 60, verify_ssl: bool = True, message: Dict = None,
                 use_zh: bool = True):
        """
        基于requests的同步封装
        Args:
            app: app应用
            timeout:request timeout
            verify_ssl:verify ssl
            message: 提示消息
            use_zh: 消息提示是否使用中文，默认中文

        """
        self.session = None
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.message = message or {}
        self.use_zh = use_zh
        self.msg_zh = None

        if app is not None:
            self.init_app(app, timeout=self.timeout, verify_ssl=self.verify_ssl, message=self.message,
                          use_zh=self.use_zh)

    def init_app(self, app, *, timeout: int = None, verify_ssl: bool = None, message: Dict = None,
                 use_zh: bool = None):
        """
        基于aiohttp的异步封装
        Args:
            app: app应用
            timeout:request timeout
            verify_ssl:verify ssl
            message: 提示消息
            use_zh: 消息提示是否使用中文，默认中文
        Returns:

        """
        self.timeout = timeout or app.config.get("ECLIENTS_HTTP_TIMEOUT", None) or self.timeout
        self.verify_ssl = verify_ssl or app.config.get("ECLIENTS_HTTP_VERIFYSSL", None) or self.verify_ssl
        message = message or app.config.get("ECLIENTS_HTTP_MESSAGE", None) or self.message
        use_zh = use_zh or app.config.get("ECLIENTS_HTTP_MSGZH", None) or self.use_zh

        self.message = verify_message(http_msg, message)
        self.msg_zh = "msg_zh" if use_zh else "msg_en"
        # 初始化session
        self.session = sync_requests.Session()

        @atexit.register
        def close_connection():
            """
            释放session连接池所有连接
            Args:

            Returns:

            """
            if self.session:
                self.session.close()

    def init_session(self, *, timeout: int = None, verify_ssl: bool = None, message: Dict = None,
                     use_zh: bool = None):
        """
        基于aiohttp的异步封装
        Args:
            timeout:request timeout
            verify_ssl:verify ssl
            message: 提示消息
            use_zh: 消息提示是否使用中文，默认中文
        Returns:

        """
        self.timeout = timeout or self.timeout
        self.verify_ssl = verify_ssl or self.verify_ssl
        use_zh = use_zh or self.use_zh
        self.message = verify_message(http_msg, message or self.message)
        self.msg_zh = "msg_zh" if use_zh else "msg_en"
        # 初始化session
        self.session = sync_requests.Session()

        @atexit.register
        def close_connection():
            """
            释放session连接池所有连接
            Args:

            Returns:

            """
            if self.session:
                self.session.close()

    def _request(self, method: str, url: str, *, params: Dict = None, data: Dict = None, json: Dict = None,
                 headers: Dict = None, verify_ssl: bool = None, timeout: int = None, **kwargs) -> Response:
        """

        Args:
            method, url, *,  params=None, data=None, json=None, headers=None, **kwargs
        Returns:

        """

        def _get():
            """

            Args:

            Returns:

            """
            return self.session.get(url, params=params, verify=verify_ssl, headers=headers,
                                    timeout=timeout, **kwargs)

        def _post():
            """

            Args:

            Returns:

            """
            res = self.session.post(url, params=params, data=data, json=json, headers=headers,
                                    verify=verify_ssl, timeout=timeout, **kwargs)
            return res

        def _put():
            """

            Args:

            Returns:

            """
            return self.session.put(url, params=params, data=data, json=json, headers=headers, verify=verify_ssl,
                                    timeout=timeout, **kwargs)

        def _patch():
            """

            Args:

            Returns:

            """
            return self.session.patch(url, params=params, data=data, json=json, headers=headers, verify=verify_ssl,
                                      timeout=timeout, **kwargs)

        def _delete():
            """

            Args:

            Returns:

            """
            return self.session.delete(url, params=params, data=data, json=json, headers=headers, verify=verify_ssl,
                                       timeout=timeout, **kwargs)

        get_resp = {"GET": _get, "POST": _post, "PUT": _put, "DELETE": _delete, "PATCH": _patch}
        try:
            resp = get_resp[method.upper()]()
            resp.raise_for_status()
        except KeyError as e:
            raise ClientError(url=url, message="error method {0}".format(str(e)))
        except (ConnectionError, ConnectTimeout) as e:
            raise ClientConnectionError(url=url, message=str(e))
        except (Timeout, HTTPError) as e:
            resp = e.response
            try:
                resp_data = resp.json()
            except (ValueError, TypeError):
                resp_data = resp.text
            raise ClientResponseError(url=url, status_code=resp.status_code, message=resp.reason, headers=resp.headers,
                                      body=resp_data)
        except RequestException as e:
            raise ClientError(url=url, message="ClientError: {}".format(vars(e)))

        with resp:
            try:
                resp_json = resp.json()
            except (ValueError, TypeError):
                context_type = resp.headers.get("Content-Type", "")
                if "text" in context_type:
                    resp_text = resp.text
                    return Response(resp.status_code, resp.reason, resp.headers, resp.cookies, resp_body=resp_text,
                                    content=b"")
                else:
                    resp_bytes = resp.content
                    return Response(resp.status_code, resp.reason, resp.headers, resp.cookies, resp_body="",
                                    content=resp_bytes)
            else:
                return Response(resp.status_code, resp.reason, resp.headers, resp.cookies, resp_body=resp_json,
                                content=b"")

    def request(self, method: str, url: str, *, params: Dict = None, data: Dict = None, json: Dict = None,
                headers: Dict = None, verify_ssl: bool = None, timeout: int = None, **kwargs) -> Response:
        """

        Args:

        Returns:

        """
        verify_ssl = self.verify_ssl if verify_ssl is None else verify_ssl
        timeout = self.timeout if timeout is None else timeout
        return self._request(method, url, params=params, data=data, json=json, headers=headers,
                             verify_ssl=verify_ssl, timeout=timeout, **kwargs)

    def get(self, url: str, *, params: Dict = None, headers: Dict = None, verify_ssl: bool = None,
            timeout: int = None, **kwargs) -> Response:
        """

        Args:

        Returns:

        """
        verify_ssl = self.verify_ssl if verify_ssl is None else verify_ssl
        timeout = self.timeout if timeout is None else timeout
        return self._request("GET", url, params=params, verify_ssl=verify_ssl, headers=headers,
                             timeout=timeout, **kwargs)

    def post(self, url: str, *, params: Dict = None, data: Dict = None, json: Dict = None, headers: Dict = None,
             verify_ssl: bool = None, timeout: int = None, **kwargs) -> Response:
        """

        Args:

        Returns:

        """
        verify_ssl = self.verify_ssl if verify_ssl is None else verify_ssl
        timeout = self.timeout if timeout is None else timeout
        return self._request("POST", url, params=params, data=data, json=json, headers=headers, verify_ssl=verify_ssl,
                             timeout=timeout, **kwargs)

    def put(self, url: str, *, params: Dict = None, data: Dict = None, json: Dict = None, headers: Dict = None,
            verify_ssl: bool = None, timeout: int = None, **kwargs) -> Response:
        """

        Args:

        Returns:

        """
        verify_ssl = self.verify_ssl if verify_ssl is None else verify_ssl
        timeout = self.timeout if timeout is None else timeout
        return self._request("PUT", url, params=params, data=data, json=json, headers=headers, verify_ssl=verify_ssl,
                             timeout=timeout, **kwargs)

    def patch(self, url: str, *, params: Dict = None, data: Dict = None, json: Dict = None, headers: Dict = None,
              verify_ssl: bool = None, timeout: int = None, **kwargs) -> Response:
        """

        Args:

        Returns:

        """
        verify_ssl = self.verify_ssl if verify_ssl is None else verify_ssl
        timeout = self.timeout if timeout is None else timeout
        return self._request("PATCH", url, params=params, data=data, json=json, headers=headers, verify_ssl=verify_ssl,
                             timeout=timeout, **kwargs)

    def delete(self, url: str, *, params: Dict = None, headers: Dict = None, verify_ssl: bool = None,
               timeout: int = None, **kwargs) -> Response:
        """

        Args:

        Returns:

        """
        verify_ssl = self.verify_ssl if verify_ssl is None else verify_ssl
        timeout = self.timeout if timeout is None else timeout
        return self._request("DELETE", url, params=params, verify_ssl=verify_ssl, headers=headers, timeout=timeout,
                             **kwargs)

    def close(self, ):
        """
        close
        Args:

        Returns:

        """
        self.session.close()
