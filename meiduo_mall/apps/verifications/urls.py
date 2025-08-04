# -*- coding: utf-8 -*-
# @Time    : 2025/8/4 16:36
# @Author  : 老冰棍
# @File    : urls.py
# @Software: PyCharm

from django.urls import path
from django.urls.converters import register_converter
from apps.verifications.views import ImageCodeView, SmsCodeView
from utils.converters import MobileConverter

register_converter(MobileConverter, 'mobile')

urlpatterns = [
    path('image_codes/<uuid>/', ImageCodeView.as_view(), name='image_code'),
    path('sms_codes/<mobile:mobile>/', SmsCodeView.as_view(), name='sms_code'),
]