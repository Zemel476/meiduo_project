import json
import re

from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from django.db import transaction

from apps.users.models import User
from celery_tasks.email.tasks import celery_send_mail
from meiduo_mall import settings
from utils.tokens import encrypt_with_expiry, decrypt_with_expiry
from utils.views import LoginRequiredJsonMixin


# Create your views here.

class UsernameCountView(View):

    def get(self, request, username, count):
        count = User.objects.filter(username=username).count()

        return JsonResponse({'count':count, 'code':0, 'msg': ''})


class RegisterView(View):

    def post(self, request):
        json_data = json.loads(request.body)

        username = json_data.get('username')
        password = json_data.get('password')
        password2 = json_data.get('password2')
        mobile = json_data.get('mobile')
        sms_code = json_data.get('sms_code')
        allow = json_data.get('allow')

        # all 里面有一个元素为False 则返回False
        if not all([username, password, password2, mobile, allow, sms_code]):
            return JsonResponse({'code': 400, 'msg': '参数异常1'})

        if not re.match(r'[a-zA-Z0-9]{5,16}', username):
            return JsonResponse({'code': 400, 'msg': '参数异常2'})

        if not re.match(r'^1[3-9]\d{9}', str(mobile)):
            return JsonResponse({'code': 400, 'msg': '参数异常3'})

        if not re.match(r'^[0-9]{5,10}', str(password)) or password != password2:
            return JsonResponse({'code': 400, 'msg': '参数异常4'})

        redis_cli = get_redis_connection('code')
        redis_sms_code = redis_cli.get(mobile)
        if redis_sms_code != sms_code:
            return JsonResponse({'code': 400, 'msg': '验证码有误！'})

        # 使用 create_user 这里密码会加密
        user = User.objects.create_user(username=username, password=str(password), mobile=mobile)
        # 注册 保持登录
        # 方法1
        # request.session['user'] = user.id

        # 方法2 django 提供的状态保持方案
        login(request, user)

        if not allow:
            request.session.set_expiry(0)

        return JsonResponse({'code': 0, 'msg': 'ok'})


class LoginView(View):

    def post(self, request):
        request_data = json.loads(request.body)
        username = request_data.get('username')
        password = request_data.get('password')
        remember = request_data.get('remember')

        if not all([username, password]) or not re.match(r'^[a-zA-Z0-9]{5,16}', username):
            return JsonResponse({'code': 400, 'msg': '账号或密码有误！'})

        if re.match(r'1[3-9]\d{9}]', str(username)):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # django 提供用户登录功能
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({'code': 400, 'msg': '账号或密码有误！'})

        # 设置用户登录状态 session
        login(request, user)
        # 设置用户session保存时间
        if remember:
            request.session.set_expiry(3600*12)
        else:
            request.session.set_expiry(0)

        response = JsonResponse({'code': 0, 'msg': 'ok'})
        response.set_cookie('username', user.username, max_age=3600*12)

        return response


class LogoutView(View):

    def delete(self, request):
        # 删除session
        logout(request)

        response = JsonResponse({'code': 0, 'msg': 'ok'})
        response.delete_cookie('username')

        return response

# LoginRequiredMixin 是 Django 的一个 类视图（Class-Based View）辅助工具，
# 用于强制用户必须登录才能访问某个视图。
# 如果未登录用户尝试访问，会自动将其重定向到登录页面（或返回 403 错误）
class CenterView(LoginRequiredJsonMixin, View):

    def get(self, request):
        info_data = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return JsonResponse({'code': 0, 'msg': 'ok', 'data': info_data})


class EmailView(View):

    def put(self, request):
        json_data = json.loads(request.body)
        email = json_data.get('email')

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return JsonResponse({'code': 400, 'msg': '邮箱格式错误!'})

        request.user.email = email
        request.user.save()

        # 发送邮件
        from_email = settings.EMAIL_FROM
        target_email = ['xxx']
        # 邮件内容
        subject = 'subject'
        # 加密跳转链接
        text_content = 'httP://127.0.0.1:8000/success_verify_email.html?token={}'.format(encrypt_with_expiry({'username': request.user.username, 'email': email}, 3600*24))

        celery_send_mail.delay(from_email, target_email, subject, text_content)

        return JsonResponse({'code': 0, 'msg': 'ok'})


class EmailVerifyView(View):

    def put(self, request):
        token = request.GET.get('token')
        if not token:
            return JsonResponse({'code': 400, 'msg': '请求异常'})

        user_dict = decrypt_with_expiry(token)
        if not user_dict:
            return JsonResponse({'code': 400, 'msg': '请求异常'})

        try:
            with transaction.atomic():
                user = User.objects.get(username=user_dict['username'], email=user_dict['email'])

                user.email_active = True
                user.save()

            return JsonResponse({'code': 0, 'msg': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'code': 400, 'msg': '请求异常'})


