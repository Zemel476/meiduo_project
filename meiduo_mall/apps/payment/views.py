from alipay import AliPay, AliPayConfig
from django.http import JsonResponse
from django.views import View

from apps.orders.models import OrderInfo
from apps.payment.models import Payment
from meiduo_mall import settings
from utils.views import LoginRequiredJsonMixin


# Create your views here.
class PayUrlView(LoginRequiredJsonMixin, View):
    def get(self,request, order_id):
        # user = request.user
        # try:
        #     order = OrderInfo.objects.get(pk=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'], user=user)
        # except OrderInfo.DoesNotExist:
        #     return JsonResponse({'code': 400, 'msg': '数据异常！'})

        app_private_key_string = open(settings.APP_PRIVATE_KEY).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY).read()

        alipay = get_api_pay(app_private_key_string, alipay_public_key_string)

        subject = '测试数据'
        order_string = alipay.api_alipay_trade_page_pay(
            # out_trade_no=order.order_id,
            out_trade_no=order_id,
            total_amount=str(1500000),  # Decimal 不是基本数据类型
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL, # 支付成功后跳转的页面
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return JsonResponse({'code': 0, 'msg': 'ok', 'alipay_url': alipay_url})


class PaymentStatusView(View):

    def put(self,request):
        data = request.GET
        signature = data.pop('sign')

        app_private_key_string = open(settings.APP_PRIVATE_KEY).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY).read()

        alipay = get_api_pay(app_private_key_string, alipay_public_key_string)

        success = alipay.verify(data, signature)
        if success:
            trade_no = data.get('trade_no') # 支付宝交易流水号
            order_id = data.get('out_trade_no') # 商品订单流水号
            try:
                order = OrderInfo.objects.get(order_id=order_id)
            except OrderInfo.DoesNotExist:
                return JsonResponse({'code': 0, 'msg': '数据异常'})
            else:
                Payment.objects.create(trade_no=trade_no, order=order)
                order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                order.save()

            return JsonResponse({'code': 0, 'msg': 'ok', 'trade_no': trade_no})

        return JsonResponse({'code': 0, 'msg': '请联系客服'})



def get_api_pay(app_private_key_string, alipay_public_key_string):
    return AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # the default notify path
        app_private_key_string=app_private_key_string,
        # alipay public key, do not use your own public key!
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA or RSA2
        debug=settings.ALIPAY_DEBUG,  # False by default
        verbose=False,  # useful for debugging
        config=AliPayConfig(timeout=15)  # optional, request timeout
    )