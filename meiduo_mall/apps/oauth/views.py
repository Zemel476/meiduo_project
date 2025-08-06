import json

from django.conf import settings
from django.contrib.auth import login
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection

from apps.oauth.models import OAuthQQUser
from apps.users.models import User


# Create your views here.
# 前端点击 qq 登录连接，发送请求给后端
# 后端生成绑定连接，返回给前端
# 获取code
# 获取token
# 获取 openid
# 保存openid

class QQLoginURLView(View):

    def get(self, request):
        state = 111 # 不知道，随便写
        qq = OAuthQQ(settings.QQ_CLIENT_ID, settings.QQ_CLIENT_SECRET, settings.REDIRECT_URL, state)
        qq_login_url = qq.get_qq_url()

        return JsonResponse({'code': 0, 'login_url': qq_login_url, 'msg': 'ok'})


class OathQQView(View):

    def get(self, request):
        # 获取code
        code = request.Get.get('code')
        if not code:
            return JsonResponse({'code': 400, 'msg': '数据异常！'})

        # 获得open id
        qq = OAuthQQ(settings.QQ_CLIENT_ID, settings.QQ_CLIENT_SECRET, settings.REDIRECT_URL, state='xxx')
        qq_token = qq.get_access_token(code)
        open_id = qq.get_open_id(access_token=qq_token)

        # 判断用户是否已绑定账号
        try:
            qq_user = OAuthQQUser.objects.get(openid=open_id)
        except OAuthQQUser.DoesNotExist:
            return JsonResponse({'code': 200, 'msg': 'ok', 'access_token': open_id})
        else: # 如果用户已绑定，直接登录
            login(request, qq_user.user)
            response = JsonResponse({'code': 0, 'msg': 'ok'})
            response.set_cookie('username', qq_user.user.username)

            return response

    def post(self, request):
        json_data = json.loads(request.body)

        mobile= json_data.get('mobile')
        password= json_data.get('password')
        sms_code= json_data.get('sms_code')
        qq_code = json_data.get('qq_code')
        access_token = json_data.get('access_token')

        if not all([mobile, password, sms_code, access_token]):
            return JsonResponse({'code':400, 'msg':'数据异常！'})

        redis_cli = get_redis_connection('code')
        if not redis_cli or sms_code != redis_cli.get('sms_code'):
            return JsonResponse({'code':400, 'msg':'短信验证码有误！'})

        qq = OAuthQQ(settings.QQ_CLIENT_ID, settings.QQ_CLIENT_SECRET, settings.REDIRECT_URL, state='xxx')
        qq_token = qq.get_access_token(qq_code)
        open_id = qq.get_open_id(access_token=qq_token)
        if open_id != access_token:
            return JsonResponse({'code': 400, 'msg': '数据异常！'})

        with transaction.atomic():
            try:
                user = User.objects.get(mobile=mobile) #判断用户是否已注册
            except User.DoesNotExist: # 用户没注册
                # 手机号不存在，帮助用户注册并绑定 open_id
                user = User.objects.create_user(username=mobile,mobile=mobile, password=str(password))
            else:
                # 手机号存在，检验密码
                if not user.check_password(password):
                    return JsonResponse({'code':400, 'msg':'您已注册该网站，请检查密码！'})

            OAuthQQUser.objects.create(openid=access_token, user=user)

        login(request, user)
        response = JsonResponse({'code': 0, 'msg': 'ok'})
        response.set_cookie('username', user.username)

        return response






