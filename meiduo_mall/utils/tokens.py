# -*- coding: utf-8 -*-
# @Time    : 2025/8/7 16:26
# @Author  : 老冰棍
# @File    : tokens.py
# @Software: PyCharm
import datetime

import jwt

from meiduo_mall import settings

def encrypt_with_expiry(data, expiry_seconds=5):
    payload = {
        'data': data,
        'exp': datetime.datetime.now() + datetime.timedelta(seconds=expiry_seconds)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# 解密并验证是否过期
def decrypt_with_expiry(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload['data']
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"