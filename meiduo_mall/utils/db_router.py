# -*- coding: utf-8 -*-
# @Time    : 2025/8/15 17:13
# @Author  : 老冰棍
# @File    : db_router.py
# @Software: PyCharm
class MasterSlaveDBRouter(object):
    """数据库读写路由"""

    def db_for_read(self, model, **hints):
        """读"""

        return 'slave'

    def db_for_write(self, model, **hints):
        """写"""

        return 'default'