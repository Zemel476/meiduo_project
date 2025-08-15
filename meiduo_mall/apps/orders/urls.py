# -*- coding: utf-8 -*-
# @Time    : 2025/8/13 17:55
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm
from django.urls import path

from apps.orders.views import OrderSettlementView, OrderCommitView

urlpatterns = [
    path('orders/settlement/', OrderSettlementView.as_view(), name='settlement'),
    path('orders/commit/', OrderCommitView.as_view(), name='commit'),
]