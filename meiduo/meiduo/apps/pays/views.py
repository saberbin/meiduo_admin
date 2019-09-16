from django.shortcuts import render
from django import http
from django.views import View
from meiduo.utils.response_code import RETCODE
from alipay import AliPay
from django.conf import settings
from .models import PayModel
from orders.models import OrderInfo


class AliPaymentView(View):
    def get(self, request, order_id):
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "订单信息不存在"})

        # 准备公钥，私钥
        app_private_key_string = open(settings.ALIPAY_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.ALIPAY_RETURN_URL,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG,
        )

        subject = "美多商城订单"

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount + order.freight),
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,
        )
        alipay_url = settings.ALIPAY_URL + "?" + order_string

        return http.JsonResponse({"code": RETCODE.OK, "alipay_url": alipay_url})


class AliOrderChangeView(View):
    def get(self, request):
        # get the data from request
        dict_data = request.GET.dict()
        sign = dict_data.pop("sign")
        trade_no = dict_data.get("trade_no")
        out_trade_no = dict_data.get("out_trade_no")

        # check the data
        if not all([sign, trade_no, out_trade_no]):
            return http.HttpResponseForbidden("非法请求")

        app_private_key_string = open(settings.ALIPAY_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.ALIPAY_RETURN_URL,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG,
        )
        success = alipay.verify(dict_data, sign)

        if not success:
            return http.HttpResponseForbidden("订单信息给篡改了。")

        # save the data to the database
        PayModel.objects.create(
            out_trade_no=out_trade_no,
            trade_no=trade_no,
        )

        OrderInfo.objects.filter(order_id=out_trade_no).update(status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])

        context = {
            "order_id": out_trade_no
        }
        return render(request, "pay_success.html", context=context)

