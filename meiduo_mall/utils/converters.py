# -*- coding: utf-8 -*-
# @Time    : 2025/8/4 10:17
# @Author  : 老冰棍
# @File    : converters.py
# @Software: PyCharm
class UsernameConverter:
    regex = "[a-zA-Z0-9]{5,16}"

    def to_python(self, value):
        return value


class MobileConverter:
    regex = "1[3-9]{9}"

    def to_python(self, value):
        return value