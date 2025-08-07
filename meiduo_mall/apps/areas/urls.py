# -*- coding: utf-8 -*-
# @Time    : 2025/8/7 18:48
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm
from django.urls import path

from apps.areas.views import AreaView,SubAreaView

urlpatterns = [
    path('areas/', AreaView.as_view(), name='areas'),
    path('areas/<id>/', SubAreaView.as_view(), name='sub_areas'),
]