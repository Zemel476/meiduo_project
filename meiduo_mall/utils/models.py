# -*- coding: utf-8 -*-
# @Time    : 2025/8/6 16:40
# @Author  : 老冰棍
# @File    : models.py
# @Software: PyCharm
from django.db import models


class BaseModel(models.Model):
    """ 为模型类补充字段 """

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')
    delete_time = models.DateTimeField(verbose_name='删除时间')

    class Meta:
        abstract = True # 说明是抽象基类，用于继承使用，数据库迁移时不会创建BaseModel表