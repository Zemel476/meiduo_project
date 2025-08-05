# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 18:17
# @Author  : 老冰棍
# @File    : __init__.py.py
# @Software: PyCharm
from celery_tasks.main import app as celery_app

__all__ = ('celery_app',)