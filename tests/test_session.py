#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 2020/7/28 上午10:44
"""
import time
import unittest

from flask import Flask

from eclients import DBClient, DialectDriver


class TestRedisClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = Flask("app")
        cls.app.config["ECLIENTS_IS_BINDS"] = True
        cls.db = DBClient(passwd="123456", dbname="edu_base")
        cls.db.init_app(cls.app)
        cls.app.config["SQLALCHEMY_BINDS"][
            'cloud_project'] = f'{DialectDriver.mysql_pymysql}://root:123456@127.0.0.1:3306/cloud_project?' \
                               f'charset=utf8mb4&binary_prefix=True'

    def test1_gen_session(self):
        class CycleProjectModel(self.db.Model):
            """
            model
            """
            __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

            __tablename__ = "cycle_project"

            id = self.db.Column(self.db.String(24), primary_key=True, nullable=False, doc='实例ID')
            project_name = self.db.Column(self.db.String(100), unique=True, nullable=False, doc='项目名称')

        class ProjectFillingScopeModel(self.db.Model):
            """
            model
            """
            __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

            __tablename__ = "project_filling_scope"

            id = self.db.Column(self.db.String(24), primary_key=True, nullable=False, doc='实例ID')
            suitable_scope_id = self.db.Column(self.db.String(24), doc='适用范围ID')

        with self.app.app_context():
            cloud_session = self.db.gen_session("cloud_project")
            print(cloud_session.query(CycleProjectModel).first())
            time.sleep(4)
            cloud_session = self.db.ping_session(cloud_session)
            print("停留4秒", cloud_session.query(CycleProjectModel).first())
            time.sleep(15)
            cloud_session = self.db.ping_session(cloud_session)
            print("停留15秒", cloud_session.query(CycleProjectModel).first())
            time.sleep(20)
            cloud_session = self.db.ping_session(cloud_session)
            print("停留20秒", cloud_session.query(CycleProjectModel).first())

            with self.db.gsession("cloud_project") as cloud_session:
                print(cloud_session.query(ProjectFillingScopeModel).first())

    def test2_default_session(self):
        class ReportTypeModel(self.db.Model):
            """
            报表类型
            """
            __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

            __tablename__ = "report_type"

            id = self.db.Column(self.db.String(24), primary_key=True, nullable=False, doc='实例ID')
            name = self.db.Column(self.db.String(100), nullable=False, doc='名称')
            description = self.db.Column(self.db.String(255), doc='描述')

        with self.app.app_context():
            # 测试默认的session
            print(self.db.session.query(ReportTypeModel).first())
            time.sleep(4)
            default_session = self.db.ping_session()
            print("停留4秒", default_session.query(ReportTypeModel).first())
            time.sleep(15)
            default_session = self.db.ping_session()
            print("停留15秒", default_session.query(ReportTypeModel).first())
            time.sleep(20)
            default_session = self.db.ping_session()
            print("停留20秒", default_session.query(ReportTypeModel).first())


if __name__ == '__main__':
    text_run = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=text_run)
