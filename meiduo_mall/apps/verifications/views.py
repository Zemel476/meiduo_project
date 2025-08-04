from django.http import HttpResponse
from django.views import View
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
