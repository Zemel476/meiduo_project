import base64
import json
import pickle
from urllib.parse import unquote

from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from redis.asyncio.utils import pipeline

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
            pipeline = redis_cli.pipeline()
            # 操作hash
            pipeline.hincrb(f'carts:{user.id}', sku_id, count)
            # 操作set
            pipeline.sadd(f'selected:{user.id}', sku_id)

            pipeline.execute()

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

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            sku_id_counts = redis_cli.hgetall(f'carts:{user.id}')
            selected_ids = redis_cli.smembers(f'selected:{user.id}')
            # 格式转换 统一数据格式
            carts = {}
            for sku_id, count in sku_id_counts.items():
                carts[str(sku_id)] = {'count': count, 'selected': sku_id in selected_ids}
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                carts = pickle.loads(base64.b64decode(unquote(cookie_carts)))
            else:
                carts = {}

        skus = SKU.objects.filter(pk__in=carts.keys()).values('id', 'price', 'name')
        result = []
        for sku in skus:
            cart =  carts.get(str(sku['id']))

            sku['count'] = cart['count']
            sku['selected'] = cart['selected']
            sku['amount'] =  sku['count'] * sku['price']
            result.append(sku)

        return JsonResponse({'code': 0, 'msg': 'ok', 'cart_skus': result})

    def put(self, request):
        json_data = json.loads(request.body)
        sku_id = json_data.get('sku_id')
        count = json_data.get('count')
        selected = json_data.get('selected')
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'msg': '数据异常'})

        try:
            SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'msg': '商品不存在'})

        try:
            count = int(count)
        except ValueError:
            count = 1

        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hset(f'carts:{user.id}', sku_id, count)
            if selected:
                redis_cli.sadd(f'selected:{user.id}', sku_id)
            else:
                redis_cli.srem(f'selected:{user.id}', sku_id)
        else:
            carts = request.COOKIES.get('carts')
            if carts:
                carts = pickle.loads(base64.b64decode(unquote(carts)))
            else:
                carts = {}

            if str(sku_id) in carts:
                carts[str(sku_id)] = {'count': count, 'selected': selected}

            response = JsonResponse({'code':0, 'msg': 'ok'})

            base64_encode = base64.b64encode(pickle.dumps(carts))
            response.set_cookie('carts', base64_encode.decode())

            return response

    def delete(self, request):
        json_data = json.loads(request.body)
        sku_id = json_data.get('sku_id')

        if not sku_id:
            return JsonResponse({'code': 400, 'msg': '数据异常！'})

        try:
            SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'msg': '商品不存在！'})

        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hdel(f'carts:{user.id}', sku_id)
            redis_cli.srem(f'selected:{user.id}', sku_id)

            return JsonResponse({'code': 0, 'msg': 'ok'})
        else:
            cookie_carts = request.COOKIES.get('carts')
            carts = pickle.loads(base64.b64decode(unquote(cookie_carts)))

            carts.pop(str(sku_id))

            response = JsonResponse({'code':0, 'msg': 'ok'})

            base64_encode = base64.b64encode(pickle.dumps(carts))
            response.set_cookie('carts', base64_encode.decode())

            return response