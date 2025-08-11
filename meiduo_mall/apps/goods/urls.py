# -*- coding: utf-8 -*-
# @Time    : 2025/8/8 16:19
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm
from django.urls import path

from apps.goods.views import IndexView, ListView, SKUSearchView

urlpatterns = [
    path('index/', IndexView.as_view(), name='index'),
    path('list/<category_id>/skus/', ListView.as_view(), name='list'),
    path('search/', SKUSearchView(), name='list'),
]