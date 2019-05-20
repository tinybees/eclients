#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-12-25 下午4:58
"""
from contextlib import contextmanager

import aelog
from flask import g, request
from flask_sqlalchemy import SQLAlchemy
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

        super().__init__(app)

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

    @contextmanager
    def insert_session(self, ):
        """
        插入数据session
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
    def update_session(self, ):
        """
        更新数据session
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
    def delete_session(self, ):
        """
        删除数据session
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
