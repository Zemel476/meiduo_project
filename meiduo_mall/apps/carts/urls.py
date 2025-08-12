# -*- coding: utf-8 -*-
# @Time    : 2025/8/12 18:36
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm
from django.urls import path

from apps.carts.views import CartsView

urlpatterns = [
    path('carts/', CartsView.as_view(), name='carts'),
]