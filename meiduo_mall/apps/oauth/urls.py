# -*- coding: utf-8 -*-
# @Time    : 2025/8/6 16:59
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm
from django.urls import path

from apps.oauth.views import QQLoginURLView, OathQQView

urlpatterns = [
    path('qq/authorization/', QQLoginURLView.as_view(), name='qq_authorization'),
    path('oauth_callback/', OathQQView.as_view(), name='qq_login'),
]