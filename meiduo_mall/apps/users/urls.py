# -*- coding: utf-8 -*-
# @Time    : 2025/8/3 21:37
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm

from django.urls import path

from apps.users.views import UsernameCountView
from django.urls import register_converter

from utils.converters import UsernameConverter

register_converter(UsernameConverter, 'username')
urlpatterns = [
    path('username/<username:username>/<int:count>', UsernameCountView.as_view(), name='username'),
]