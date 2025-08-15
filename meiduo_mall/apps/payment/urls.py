# -*- coding: utf-8 -*-
# @Time    : 2025/8/14 19:45
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm
from django.urls import path

from apps.payment.views import PayUrlView, PaymentStatusView

urlpatterns = [
    path('payments/status/', PaymentStatusView.as_view(), name='paymentStatus'),
    path('payments/<order_id>/', PayUrlView.as_view(), name='payments'),
]