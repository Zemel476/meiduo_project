# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 18:31
# @Author  : 老冰棍
# @File    : tasks.py
# @Software: PyCharm
from ronglian_sms_sdk import SmsSDK
from celery_tasks.main import app


# 任务文件名称一定要是 tasks.py
# 这个函数 必须要让celery的实例的 task装饰器装饰


@app.task
def celery_send_sms_code(mobile, sms_code, expire_time):
    acc_id = 'xxx'  # 容联云通讯分配的主账号ID
    acc_token = 'xxxx'  # 容联云通讯分配的主账号TOKEN
    app_id = 'xxx'  # 容联云通讯分配的应用ID

    SmsSDK(acc_id, acc_token, app_id).sendMessage('1', mobile, (sms_code, expire_time))
