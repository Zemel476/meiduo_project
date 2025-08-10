# -*- coding: utf-8 -*-
# @Time    : 2025/8/10 18:04
# @Author  : 老冰棍
# @File    : storage.py
# @Software: PyCharm

from django.core.files.storage import Storage

# 自定义文件存储类
class StaticFilesStorage(Storage):

    def open(self, name, mode="rb"):
        """Retrieve the specified file from storage."""
        pass

    def save(self, name, content, max_length=None):
        pass

    def url(self, name):
        return 'http://127.0.0.1:8000/' + name