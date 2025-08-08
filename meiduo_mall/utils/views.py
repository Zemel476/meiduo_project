# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 21:29
# @Author  : 老冰棍
# @File    : views.py
# @Software: PyCharm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

# LoginRequiredMixin 是 Django 的一个 类视图（Class-Based View）辅助工具，
# 用于强制用户必须登录才能访问某个视图。
# 如果未登录用户尝试访问，会自动将其重定向到登录页面（或返回 403 错误）
class LoginRequiredJsonMixin(LoginRequiredMixin):

    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'msg': '账号未登录'})