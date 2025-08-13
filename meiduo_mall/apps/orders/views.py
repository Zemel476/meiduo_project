import json
from decimal import Decimal

from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo
from apps.users.models import Address
from utils.views import LoginRequiredJsonMixin


# Create your views here.
class OrderSettlementView(LoginRequiredJsonMixin, View):

    def get(self, request):
        user = request.user
        addresses = Address.objects.filter(user=user, is_deleted=False).values('id', 'province', 'city','place')
        address_list = [address for address in addresses]

        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        pipeline.hgetall(f'carts:{user.id}')
        pipeline.smembers(f'selected:{user.id}')
        # 接收 管道统一执行后返回的结果
        result = pipeline.execute()

        sku_ids = result[0]
        selected_sku_ids = result[1]

        selected_carts = { int(sku_id) : int(sku_ids.get(sku_id)) for sku_id in selected_sku_ids}

        skus = SKU.objects.filter(id__in=selected_sku_ids).values('id', 'name', 'price')

        sku_list = []
        for sku in skus:
            sku['count'] = selected_carts[sku['sku_id']]
            sku_list.append(sku)

        context = {
            'skus': sku_list,
            'address_list': address_list,
            'freight': Decimal('10.00'),
        }

        return JsonResponse({'code': 0, 'msg': '', 'context': context})


class OrderCommitView(LoginRequiredJsonMixin, View):

    def post(self, request):
        user = request.user
        json_data = json.loads(request.body)
        address_id = json_data.get('address_id')
        pay_method = json_data.get('pay_method')

        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'msg': '参数异常！'})

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'msg': '参数异常！'})

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'msg': '参数异常！'})

        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + f'{user.id}9d'

        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            pay_status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            pay_status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        total_count = 0
        total_amount = Decimal('0.00')
        freight = Decimal('10.00')

        OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            pay_method=pay_method,
            status=pay_status,
            total_count=total_count,
            total_amount=total_amount,
            freight=freight,
        )

