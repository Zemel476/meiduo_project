import json
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
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

        with transaction.atomic():
            # 设置事务回滚点
            point = transaction.savepoint()

            # 生成订单基本信息
            order_info = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                pay_method=pay_method,
                status=pay_status,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
            )

            # 从redis中取出已勾选商品信息
            redis_cli = get_redis_connection('carts')
            sku_id_counts = redis_cli.hgetall(f'carts:{user.id}')

            selected_ids = redis_cli.smembers(f'selected:{user.id}')

            carts = {}
            for sku_id in selected_ids:
                carts[int(sku_id)] = int(sku_id_counts.get(sku_id))

            # 取出商品信息 校验商品数量，进行商品加总
            skus = SKU.objects.filter(pk__in=carts.keys())
            for sku in skus:
                count = carts.get(sku.id)
                if sku.stock < count:
                    # 回滚点
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code': 400, 'msg':'商品数量不足！'})

                old_stock = sku.stock

                sku.stock -= count
                sku.sales += count
                # 乐观锁，防止超卖
                result = SKU.objects.filter(id=sku.id, stock=old_stock).update(stock=sku.stock, sales=sku.sales)
                if not result:
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code':400, 'msg': '下单失败'})

                order_info.total_count += count
                order_info.total_amount += (count * sku.price)

                # 保留订单商品信息
                OrderGoods.objects.create(
                    order=order_info,
                    sku=sku,
                    count=count,
                    price=sku.price,
                )

            order_info.total_amount += freight
            order_info.save()

        # 清除redis 已勾选商品信息
        pipeline = redis_cli.pipeline()
        pipeline.hdel(f'carts:{user.id}', *selected_ids)

        pipeline.srem(f'selected:{user.id}', *selected_ids)
        pipeline.execute()

        return JsonResponse({'code': 0, 'msg': 'ok', 'order_id': order_id})
