#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-12-25 下午4:58
"""
from contextlib import contextmanager

import aelog
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError, IntegrityError

from .err_msg import mysql_msg
from .exceptions import HttpError, MysqlDuplicateKeyError, MysqlError
from .utils import verify_message

__all__ = ("MysqlClient",)


class MysqlClient(SQLAlchemy):
    """
    MySQL同步操作指南
    """

    def __init__(self, app=None, *, username="root", passwd=None, host="127.0.0.1", port=3306, dbname=None,
                 pool_size=50, **kwargs):
        """
        MySQL同步操作指南
        Args:
            app: app应用
            host:mysql host
            port:mysql port
            dbname: database name
            username: mysql user
            passwd: mysql password
            pool_size: mysql pool size
        """
        self.username = username
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dbname = dbname
        self.pool_size = pool_size
        self.message = kwargs.get("message", {})
        self.use_zh = kwargs.get("use_zh", True)
        self.msg_zh = None
        self._app = None

        super().__init__(app)

    def init_app(self, app, username=None, passwd=None, host=None, port=None, dbname=None, pool_size=None, **kwargs):
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

        Returns:

        """
        username = username or app.config.get("ECLIENTS_MYSQL_USERNAME", None) or self.username
        passwd = passwd or app.config.get("ECLIENTS_MYSQL_PASSWD", None) or self.passwd
        host = host or app.config.get("ECLIENTS_MYSQL_HOST", None) or self.host
        port = port or app.config.get("ECLIENTS_MYSQL_PORT", None) or self.port
        dbname = dbname or app.config.get("ECLIENTS_MYSQL_DBNAME", None) or self.dbname
        pool_size = pool_size or app.config.get("ECLIENTS_MYSQL_POOL_SIZE", None) or self.pool_size
        message = kwargs.get("message") or app.config.get("ECLIENTS_MYSQL_MESSAGE", None) or self.message
        use_zh = kwargs.get("use_zh") or app.config.get("ECLIENTS_MYSQL_MSGZH", None) or self.use_zh

        passwd = passwd if passwd is None else str(passwd)
        self.message = verify_message(mysql_msg, message)
        self.msg_zh = "msg_zh" if use_zh else "msg_en"

        app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://{}:{}@{}:{}/{}".format(
            username, passwd, host, port, dbname)
        app.config['SQLALCHEMY_POOL_SIZE'] = pool_size
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600

        super().init_app(app)

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
                raise MysqlDuplicateKeyError(e)
            else:
                raise MysqlError(e)
        except DatabaseError as e:
            self.session.rollback()
            aelog.exception(e)
            raise MysqlError(e)
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
                raise MysqlDuplicateKeyError(e)
            else:
                raise MysqlError(e)
        except DatabaseError as e:
            self.session.rollback()
            aelog.exception(e)
            raise MysqlError(e)
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
            raise MysqlError(e)
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
                raise MysqlDuplicateKeyError(e)
            else:
                raise MysqlError(e)
        except DatabaseError as e:
            self.session.rollback()
            aelog.exception(e)
            raise MysqlError(e)
        except Exception as e:
            self.session.rollback()
            aelog.exception(e)
            raise HttpError(500, message=self.message[2][self.msg_zh], error=e)
        else:
            return cursor.fetchall()
