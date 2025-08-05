import json
import random

from django.http import HttpResponse, JsonResponse
from django.views import View
from ronglian_sms_sdk import SmsSDK

from libs.captcha.captcha import captcha
from django_redis import get_redis_connection


# Create your views here.
class ImageCodeView(View):

    def get(self,request, uuid):
        # text 是图片验证码内容，image 是二进制图片
        text, image = captcha.generate_captcha()

        # 让redis保存到2号库
        redis_cli = get_redis_connection('code')
        redis_cli.setex(uuid, 60, text) # name time value

        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):

    def get(self,request, mobile):
        # image_code = request.GET.get('code')
        # uuid = request.GET.get('mobile')
        #
        # if not all([image_code, uuid]):
        #     return JsonResponse({'code':400, 'msg': '参数异常'})
        #
        # # 连接redis， 校验图片验证码是否正确
        redis_cli = get_redis_connection('code')
        # redis_image_code = redis_cli.get(uuid)
        # if not redis_image_code or redis_image_code.upper() != image_code.upper():
        #     return JsonResponse({'code': 400, 'msg': '图片验证码有误'})

        # 避免频繁发送验证码
        send_flag = redis_cli.get(f'send_flag_{mobile}')
        if not send_flag:
            return JsonResponse({'code': 400, 'msg': '不要频繁发送短信'})

        # 生成4位短信验证码
        sms_code = '%04d' % random.randint(0, 9999)

        # 添加管道，使用管道收集指令
        pipeline = redis_cli.pipeline()
        # 保存短信验证码
        pipeline.setex(mobile, 60, sms_code)
        # 设置短信标记
        pipeline.setex(f'send_flag_{mobile}', 60, 1)
        # 执行指令
        pipeline.execute()

        json_result = self._send_sms(mobile, sms_code)
        if json_result['statusCode'] != '000000':
            return JsonResponse({'code': 400, 'msg': '短信发送失败！'})

        return JsonResponse({'code': 0, 'msg': '短信发送成功！'})

    @staticmethod
    def _send_sms(mobile, sms_code):
        acc_id = 'xxx'  # 容联云通讯分配的主账号ID
        acc_token = 'xxx'  # 容联云通讯分配的主账号TOKEN
        app_id = 'xxx'  # 容联云通讯分配的应用ID

        result = SmsSDK(acc_id, acc_token, app_id).sendMessage('1', mobile, (sms_code, 1))
        return json.loads(result)
