import base64
import json
import pickle
from urllib.parse import unquote

from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU


# Create your views here.
class CartsView(View):

    def post(self, request):
        json_data = json.loads(request.body)
        sku_id = json_data.get('sku_id')
        count = json_data.get('count')
        selected = json_data.get('selected')

        # try:
        #     SKU.objects.get(id=sku_id)
        # except SKU.DoesNotExist:
        #     return JsonResponse({'code': 400, 'msg': '查无此商品'})

        try:
            count = int(count)
        except ValueError:
            count = 1

        user = request.user
        # 判断用户是否登录
        if user.is_authenticated: #登录
            redis_cli = get_redis_connection('carts')
            # 操作hash
            redis_cli.hset(f'carts:{user.id}', sku_id, count)
            # 操作set
            redis_cli.sadd(f'selected:{user.id}', sku_id)

            return JsonResponse({'code':0, 'msg':'ok'})
        else: # 未登录
            response = JsonResponse({'code': 0, 'msg': 'ok'})
            cookie_carts = request.COOKIES.get('carts')

            if cookie_carts:
                carts = pickle.loads(base64.b64decode(unquote(cookie_carts)))
            else:
                carts = {}

            if str(sku_id) in carts:
                sku_data = carts.get(str(sku_id))
                sku_data['count'] += count
                sku_data['selected'] = selected
            else:
                carts[str(sku_id)] = {'count': count, 'selected': selected}

            base64_encode = base64.b64encode(pickle.dumps(carts))

            response.set_cookie('carts', base64_encode.decode(), 60)

            return response


    def get(self):
        pass


    def put(self, request):
        pass


    def delete(self, request):
        pass