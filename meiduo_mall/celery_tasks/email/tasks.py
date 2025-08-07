# -*- coding: utf-8 -*-
# @Time    : 2025/8/7 18:10
# @Author  : 老冰棍
# @File    : tasks.py
# @Software: PyCharm
from django.core.mail import send_mail

from celery_tasks.main import app


@app.task
def celery_send_mail(from_email, target_email, subject, text_content=None, html_content=None):
    # 发送邮件
    send_mail(from_email=from_email, recipient_list=target_email, subject=subject, message=text_content, html_message=html_content)
