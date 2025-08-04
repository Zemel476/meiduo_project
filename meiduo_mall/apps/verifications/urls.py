# -*- coding: utf-8 -*-
# @Time    : 2025/8/4 16:36
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm

from django.urls import path

from apps.verifications.views import ImageCodeView

urlpatterns = [
    path('image_codes/<uuid>/', ImageCodeView.as_view(), name='image_code'),
]