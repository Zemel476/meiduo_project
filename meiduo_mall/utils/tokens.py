# -*- coding: utf-8 -*-
# @Time    : 2025/8/7 16:26
# @Author  : 老冰棍
# @File    : tokens.py
# @Software: PyCharm
from itsdangerous import Serializer, BadData

from meiduo_mall import settings


def generate_reset_token(params):
    serialize = Serializer(secret_key=settings.SECRET_KEY)
    token = serialize.dumps(params)

    return token


def verify_reset_token(token):
    serializer = Serializer(settings.SECRET_KEY)
    try:
        return serializer.loads(token)
    except Exception:
        return None