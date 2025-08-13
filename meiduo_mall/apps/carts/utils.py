# -*- coding: utf-8 -*-
# @Time    : 2025/8/13 17:28
# @Author  : 老冰棍
# @File    : utils.py
# @Software: PyCharm
import base64
import pickle
from email.utils import unquote

from django_redis import get_redis_connection


def merge_cart_to_redis(request, response):
    cookie_cart = request.COOKIES.get('cart')
    if not cookie_cart:
        return

    carts = pickle.loads(base64.b64decode(unquote(cookie_cart)))

    cookie_dict = {}
    selected_ids = []
    unselected_ids = []
    for sku_id, value in carts.items():
        if value.get('selected'):
            selected_ids.append(sku_id)
        else:
            unselected_ids.append(sku_id)

        cookie_dict[sku_id] = value.get('count')

    redis_cli = get_redis_connection('carts')
    pipeline = redis_cli.pipeline()
    pipeline.hmset(f'carts:{request.user.id}', cookie_dict)


    if len(selected_ids) > 0:
        pipeline.sadd(f'carts:{request.user.id}', *selected_ids)

    if len(unselected_ids) > 0:
        pipeline.srem(f'carts:{request.user.id}', *unselected_ids)

    pipeline.execute()

    response.delete_cookie('carts')

    return response