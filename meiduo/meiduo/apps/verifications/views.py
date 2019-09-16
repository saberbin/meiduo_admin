from django.shortcuts import render
from django.views import View
from meiduo.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from meiduo.libs.yuntongxun.sms import CCP
import random
from meiduo.utils import my_constants
from users.models import User
from meiduo.utils.my_openid import decode_openid, encode_openid
from meiduo.utils import my_constants
from meiduo.utils.response_code import RETCODE


# 图形验证码
class ImageCodeView(View):
    def get(self, request, image_code_id):
        name, text, image_data = captcha.generate_captcha()

        redis_conn = get_redis_connection("code")
        redis_conn.set("image_code_%s" % image_code_id, text, my_constants.IMAGE_CODE_EXPIRE)
        print("图形验证码：", image_code_id, text)

        response = http.HttpResponse(image_data)
        response["Content-Type"] = "image/png"
        return response


# 2, 短信验证码
class SMSCodeView(View):
    def get(self, request, mobile):
        # 1,获取参数
        image_code = request.GET.get("image_code")
        image_code_id = request.GET.get("image_code_id")

        # 1,1获取短信标记,判断是否能发送
        redis_conn = get_redis_connection("code")
        flag = redis_conn.get("send_flag_%s" % mobile)
        if flag:
            return http.JsonResponse({"errmsg": "频繁发送短信"}, status=400)

        # 2,校验参数
        # 2,1 为空校验
        if not all([image_code, image_code_id]):
            return http.JsonResponse({"errmsg": "参数不全"}, status=400)

        # 2,2 图片验证码校验,是否过期
        redis_image_code = redis_conn.get("image_code_%s" % image_code_id)

        if not redis_image_code:
            return http.JsonResponse({"errmsg": "图片验证码已过期"}, status=400)

        # 删除图片验证码
        redis_conn.delete("image_code_%s" % image_code_id)

        # 判断正确性
        if image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({"errmsg": "图片验证码错误"}, status=400)

        # 3,发送短信
        sms_code = "%06d" % random.randint(0, 999999)  # 利用随机数构造短信验证码
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, 5], 1)

        # 使用celery发送短信
        # from celery_tasks.sms.tasks import send_msg_code
        # send_msg_code.delay(mobile,sms_code)

        print("sms_code = %s" % sms_code)

        # 3,1保存短信到redis中
        pipeline = redis_conn.pipeline()  # 开启管道(事务)
        pipeline.set("sms_code_%s" % mobile, sms_code, my_constants.SMS_CODE_EXPIRY)
        pipeline.set("send_flag_%s" % mobile, "flag", my_constants.SMS_CODE_SEND_FLAG)  # 设置发送标记
        pipeline.execute()  # 提交管道(事务)

        # 4,返回响应
        return http.JsonResponse({"code":0,"errmsg":"发送成功"})


# 找回密码的用户验证
class FindPasswordCheckView(View):
    def get(self, request, username):
        image_code = request.GET.get("text")
        image_code_id = request.GET.get("image_code_id")

        # check the data is exist or not
        if not all([image_code_id, image_code]):
            return http.JsonResponse({"code": RETCODE.NODATAERR}, status=400)

        # get the redis connect
        redis_conn = get_redis_connection("code")

        redis_image_code = redis_conn.get("image_code_%s" % image_code_id)

        if not redis_image_code:
            return http.JsonResponse({"errmsg": "验证码已过期"}, status=400)

        redis_conn.delete("image_code%s" % image_code_id)  # 删除库中的image_code_id数据
        if redis_image_code.decode().lower() != image_code.lower():
            return http.JsonResponse({"errmsg": "验证码不正确"}, status=400)

        # check the user in the mysql database
        count = User.objects.filter(username=username).count()
        if count == 0:
            return http.JsonResponse({"errmsg": "用户或手机号不存在"}, status=404)

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            return http.JsonResponse({"errmsg": "用户或手机号不存在"}, status=404)

        # make a access_token by username
        access_token = encode_openid(username)

        mobile = user.mobile
        return http.JsonResponse({
            "mobile": mobile,
            "access_token": access_token,
        })

# 找回密码的短信发送
class FindPasswordSendSmsCodeView(View):
    def get(self, request):
        access_token = request.GET.get("access_token")
        if not all([access_token]):
            return http.JsonResponse({"message": "已过期，请重新操作"})

        username = decode_openid(access_token)
        if not username:
            return http.JsonResponse({"message": "已过期，请重新操作"})

        user = User.objects.get(username=username)
        mobile = user.mobile

        # make a sms code by random
        sms_code = "%06d" % random.randint(0, 999999)

        # 发送短信验证码
        # ccp = CCP()
        # flag = ccp.send_template_sms(mobile, [sms_code, 5], 1)  # 5min内有效
        # 发送成功返回0，否则返回-1

        redis_conn = get_redis_connection("code")
        redis_conn.set("sms_code_%s" % mobile, sms_code, my_constants.SMS_CODE_EXPIRY)  # 300s = 5min
        redis_conn.set("send_flag_%s" % mobile, "flag", 60)  # set the send sms flag
        print("sms_code_%s" % mobile, sms_code)

        return http.JsonResponse({"code": 0, "errmsg": "发送成功"})


# 找回密码的短信验证码校验
class FPSmsCodeVCheckView(View):
    def get(self, request, username):
        if not all([username]):
            return http.JsonResponse({"errmsg": "参数不全"}, status=400)

        sms_code = request.GET.get("sms_code")
        access_token = encode_openid(username)

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            return http.JsonResponse({"errmsg": "用户或手机号不存在"}, status=404)

        # get the user information from mysql database
        mobile = user.mobile
        user_id = user.id

        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s" % mobile)

        # 检查短信验证码是否正确
        if sms_code != redis_sms_code.decode():
            return http.JsonResponse({"errmsg": "验证码不正确"}, status=400)

        return http.JsonResponse({
            "user_id": user_id,
            "access_token": access_token,
        })

