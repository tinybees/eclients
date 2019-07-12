#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-12-25 下午4:58
"""
from collections import MutableSequence
from contextlib import contextmanager

import aelog
from flask import abort, g, request
from flask_sqlalchemy import BaseQuery, Pagination, SQLAlchemy
from sqlalchemy.exc import DatabaseError, IntegrityError

from .err_msg import mysql_msg
from .exceptions import DBDuplicateKeyError, DBError, HttpError
from .utils import verify_message

__all__ = ("DBClient",)


class DBClient(SQLAlchemy):
    """
    DB同步操作指南
    """

    def __init__(self, app=None, *, username="root", passwd=None, host="127.0.0.1", port=3306, dbname=None,
                 pool_size=50, is_binds=False, bind_name="project_id", binds=None, **kwargs):
        """
        DB同步操作指南
        Args:
            app: app应用
            host:mysql host
            port:mysql port
            dbname: database name
            username: mysql user
            passwd: mysql password
            pool_size: mysql pool size
            is_binds: Whether to bind same table different database, default false
            bind_name: Binding key identifier,get from request,default project_id
            binds : Binds corresponds to  SQLALCHEMY_BINDS
            bind_func: Get the implementation logic of the bound value
        """
        self.username = username
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dbname = dbname
        self.pool_size = pool_size
        self.is_binds = is_binds
        self.bind_name = bind_name
        self.binds = binds or {}
        self.bind_func = kwargs.get("bind_func", None)
        self.message = kwargs.get("message", {})
        self.use_zh = kwargs.get("use_zh", True)
        self.msg_zh = None
        self._app = None

        # 这里要用重写的BaseQuery, 根据BaseQuery的规则,Model中的query_class也需要重新指定为子类model,
        # 但是从Model的初始化看,如果Model的query_class为None的话还是会设置为和Query一致，符合要求
        super().__init__(app, query_class=CustomBaseQuery)

    def init_app(self, app, username=None, passwd=None, host=None, port=None, dbname=None, pool_size=None,
                 is_binds=None, bind_name="", binds=None, **kwargs):
        """
        mysql 实例初始化

        Args:
            app: app应用
            host:mysql host
            port:mysql port
            dbname: database name
            username: mysql user
            passwd: mysql password
            pool_size: mysql pool size
            is_binds: Whether to bind same table different database, default false
            bind_name: Binding key identifier,get from request
            binds : Binds corresponds to  SQLALCHEMY_BINDS

        Returns:

        """
        username = username or app.config.get("ECLIENTS_MYSQL_USERNAME", None) or self.username
        passwd = passwd or app.config.get("ECLIENTS_MYSQL_PASSWD", None) or self.passwd
        host = host or app.config.get("ECLIENTS_MYSQL_HOST", None) or self.host
        port = port or app.config.get("ECLIENTS_MYSQL_PORT", None) or self.port
        dbname = dbname or app.config.get("ECLIENTS_MYSQL_DBNAME", None) or self.dbname
        pool_size = pool_size or app.config.get("ECLIENTS_MYSQL_POOL_SIZE", None) or self.pool_size
        binds = binds or app.config.get("ECLIENTS_BINDS", None) or self.binds
        message = kwargs.get("message") or app.config.get("ECLIENTS_MYSQL_MESSAGE", None) or self.message
        use_zh = kwargs.get("use_zh") or app.config.get("ECLIENTS_MYSQL_MSGZH", None) or self.use_zh
        self.is_binds = is_binds or app.config.get("ECLIENTS_IS_BINDS", None) or self.is_binds
        self.bind_name = bind_name or app.config.get("ECLIENTS_BIND_NAME", None) or self.bind_name
        self.bind_func = kwargs.get("bind_func", None) or self.bind_func

        passwd = passwd if passwd is None else str(passwd)
        self.message = verify_message(mysql_msg, message)
        self.msg_zh = "msg_zh" if use_zh else "msg_en"

        app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://{}:{}@{}:{}/{}".format(
            username, passwd, host, port, dbname)
        app.config['SQLALCHEMY_BINDS'] = binds
        app.config['SQLALCHEMY_POOL_SIZE'] = pool_size
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600

        def set_bind_key():
            """
            如果绑定多个数据库标记为真，则初始化engine之前需要设置g的绑定数据库键，防止查询的是默认的SQLALCHEMY_DATABASE_URI

            这部分的具体逻辑交给具体的业务，通过实例的bind_func来实现
            Args:

            Returns:

            """
            if self.is_binds:
                if self.bind_func and callable(self.bind_func):
                    self.bind_func()
                else:
                    # 默认实现逻辑
                    # 从header和args分别获取bind_name的值，优先获取header
                    bind_value = request.headers.get(self.bind_name) or request.args.get(self.bind_name) or None
                    bind_value = bind_value if bind_value in app.config['SQLALCHEMY_BINDS'] else None
                    setattr(g, "bind_key", bind_value)

        # Registers a function to be first run before the first request
        app.before_first_request_funcs.insert(0, set_bind_key)
        super().init_app(app)

    def get_engine(self, app=None, bind=None):
        """Returns a specific engine."""
        # dynamic bind database
        bind = g.bind_key if self.is_binds and getattr(g, "bind_key", None) else bind
        return super().get_engine(app=app, bind=bind)

    def save(self, model_obj):
        """
        保存model对象
        Args:
            model_obj: model对象
        Returns:

        """
        self.session.add(model_obj)

    def save_all(self, model_objs: MutableSequence):
        """
        保存model对象
        Args:
            model_objs: model对象
        Returns:

        """
        if not isinstance(model_objs, MutableSequence):
            raise ValueError(f"model_objs应该是MutableSequence类型的")
        self.session.add_all(model_objs)

    def delete(self, model_obj):
        """
        删除model对象
        Args:
            model_obj: model对象
        Returns:

        """
        self.session.delete(model_obj)

    @contextmanager
    def insert_context(self, ):
        """
        插入数据context
        Args:

        Returns:

        """
        try:
            yield self
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            if "Duplicate" in str(e):
                raise DBDuplicateKeyError(e)
            else:
                raise DBError(e)
        except DatabaseError as e:
            self.session.rollback()
            aelog.exception(e)
            raise DBError(e)
        except Exception as e:
            self.session.rollback()
            aelog.exception(e)
            raise HttpError(500, message=self.message[1][self.msg_zh], error=e)

    @contextmanager
    def update_context(self, ):
        """
        更新数据context
        Args:

        Returns:

        """
        try:
            yield self
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            if "Duplicate" in str(e):
                raise DBDuplicateKeyError(e)
            else:
                raise DBError(e)
        except DatabaseError as e:
            self.session.rollback()
            aelog.exception(e)
            raise DBError(e)
        except Exception as e:
            self.session.rollback()
            aelog.exception(e)
            raise HttpError(500, message=self.message[2][self.msg_zh], error=e)

    @contextmanager
    def delete_context(self, ):
        """
        删除数据context
        Args:

        Returns:

        """
        try:
            yield self
            self.session.commit()
        except DatabaseError as e:
            self.session.rollback()
            aelog.exception(e)
            raise DBError(e)
        except Exception as e:
            self.session.rollback()
            aelog.exception(e)
            raise HttpError(500, message=self.message[3][self.msg_zh], error=e)

    def execute(self, query):
        """
        插入数据，更新或者删除数据
        Args:
            query: SQL的查询字符串或者sqlalchemy表达式
        Returns:
            不确定执行的是什么查询，直接返回ResultProxy实例
        """
        try:
            cursor = self.session.execute(query)
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            if "Duplicate" in str(e):
                raise DBDuplicateKeyError(e)
            else:
                raise DBError(e)
        except DatabaseError as e:
            self.session.rollback()
            aelog.exception(e)
            raise DBError(e)
        except Exception as e:
            self.session.rollback()
            aelog.exception(e)
            raise HttpError(500, message=self.message[2][self.msg_zh], error=e)
        else:
            return cursor.fetchall()

    insert_session = insert_context
    update_session = update_context
    delete_session = delete_context


class CustomBaseQuery(BaseQuery):
    """
    改造BaseQuery,使得符合业务中使用

    目前是改造如果limit传递为0，则返回所有的数据，这样业务代码中就不用更改了
    """

    def paginate(self, page=None, per_page=None, error_out=True, max_per_page=None):
        """Returns ``per_page`` items from page ``page``.

        If ``page`` or ``per_page`` are ``None``, they will be retrieved from
        the request query. If ``max_per_page`` is specified, ``per_page`` will
        be limited to that value. If there is no request or they aren't in the
        query, they default to 1 and 20 respectively.

        When ``error_out`` is ``True`` (default), the following rules will
        cause a 404 response:

        * No items are found and ``page`` is not 1.
        * ``page`` is less than 1, or ``per_page`` is negative.
        * ``page`` or ``per_page`` are not ints.

        When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
        1 and 20 respectively.

        Returns a :class:`Pagination` object.
        """

        if request:
            if page is None:
                try:
                    page = int(request.args.get('page', 1))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    page = 1

            if per_page is None:
                try:
                    per_page = int(request.args.get('per_page', 20))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    per_page = 20
        else:
            if page is None:
                page = 1

            if per_page is None:
                per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            if error_out:
                abort(404)
            else:
                page = 1

        if per_page < 0:
            if error_out:
                abort(404)
            else:
                per_page = 20

        # 如果per_page为0,则证明要获取所有的数据，否则还是通常的逻辑
        items = self.limit(per_page).offset((page - 1) * per_page).all() if per_page != 0 else self.all()

        if not items and page != 1 and error_out:
            abort(404)

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)
