import json
import re

from django.http import JsonResponse
from django.views import View

from apps.users.models import User


# Create your views here.

class UsernameCountView(View):

    def get(self, request, username, count):
        count = User.objects.filter(username=username).count()

        return JsonResponse({'count':count, 'code':0, 'msg': ''})


class RegisterView(View):

    def post(self, request):
        json_data = json.loads(request.body)
        print(json_data)

        username = json_data.get('username')
        password = json_data.get('password')
        password2 = json_data.get('password2')
        mobile = json_data.get('mobile')
        allow = json_data.get('allow')

        # all 里面有一个元素为False 则返回False
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'msg': '参数异常1'})

        if not re.match(r'[a-zA-Z0-9]{5,16}', username):
            return JsonResponse({'code': 400, 'msg': '参数异常2'})

        if not re.match(r'^1[3-9]\d{9}', str(mobile)):
            return JsonResponse({'code': 400, 'msg': '参数异常3'})

        if not re.match(r'^[0-9]{5,10}', str(password)) or password != password2:
            return JsonResponse({'code': 400, 'msg': '参数异常4'})

        if not allow:
            return JsonResponse({'code': 400, 'msg': '参数异常5'})

        # 使用 create_user 这里密码会加密
        User.objects.create_user(username=username, password=str(password), mobile=mobile)

        return JsonResponse({'code': 0, 'msg': 'ok'})

