# -*- coding: utf-8 -*-
# @Time    : 2025/8/3 21:37
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm

from django.urls import path

from apps.users.views import UsernameCountView, RegisterView, LoginView, LogoutView, CenterView, EmailView, \
    EmailVerifyView, AddressView, UserHistoryView
from django.urls import register_converter

from utils.converters import UsernameConverter

register_converter(UsernameConverter, 'username')
urlpatterns = [
    path('usernames/<username:username>/<count>/', UsernameCountView.as_view(), name='username'),
    path('registers/', RegisterView.as_view(), name='register'),
    path('authorizations/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='login'),
    path('infos/', CenterView.as_view(), name='center'),
    path('emails/', EmailView.as_view(), name='email'),
    path('emails/verifications/', EmailVerifyView.as_view(), name='email_verify'),
    path('address/', AddressView.as_view(), name='address'),
    path('userhistories/', UserHistoryView.as_view(), name='history'),
]