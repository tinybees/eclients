#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 19-3-23 下午12:30
"""
import unittest

from eclients import RedisClient


class TestRedisClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rc = RedisClient(passwd="123456")
        cls.rc.init_engine()

    def test1_save_usual_data(self):
        data = self.rc.save_update_usual_data("usual_data", "test string")
        self.assertEqual(data, "usual_data")

    def test2_get_usual_data(self):
        data = self.rc.get_usual_data("usual_data")
        self.assertEqual(data, "test string")

    def test3_get_keys(self):
        data = self.rc.get_keys("usua*data")
        self.assertEqual(data, ["usual_data"])


if __name__ == '__main__':
    text_run = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=text_run)
