# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 18:18
# @Author  : 老冰棍
# @File    : main.py
# @Software: PyCharm
import os

from celery import Celery

# 为celery 允许设置Django运行环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

# 创建celery实例
# 参数1：main  设置脚本路径就行。脚本路径唯一。
app = Celery('celery_tasks')

# 通过加载配置文件设置 broker(中间人，队列)
app.config_from_object('celery_tasks.config')

# 需要celery 自动检测包的任务
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])


# 启动消费任务， 在控制台执行命令
#  Windows 不支持原生 Celery 的 prefork 模式, 需要使用并发模式 -P eventlet
# celery -A celery_tasks.main worker -l INFO -P eventlet