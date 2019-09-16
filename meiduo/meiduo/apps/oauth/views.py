from django.contrib.auth import login,authenticate
from django.shortcuts import render,redirect
from django.views import View
from django import http
from django.conf import settings
from QQLoginTool.QQtool import OAuthQQ
from .models import OAuthQQUser, OAuthSinaUser
from meiduo.utils.my_openid import encode_openid,decode_openid
from django_redis import get_redis_connection
from users.models import User
from carts.utils import merge_cookie_redis_data
from meiduo.utils import sinaweibopy3
import json
import re


# 获取qq登录页面
class QQLoginView(View):
    def get(self, request):
        # 1,创建qq对象
        oauth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                           client_secret=settings.QQ_CLIENT_SECRET,
                           redirect_uri=settings.QQ_REDIRECT_URI,
                           state='/')
        login_url = oauth_qq.get_qq_url()

        return http.JsonResponse({
            "login_url": login_url
        })


# 获取qq openid
class OAuthCallBackView(View):
    def get(self, request):
        # 获取code
        code = request.GET.get("code")
        if not code:
            return http.HttpResponseForbidden("code丢失")

        # 获取access_token
        oauth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                           client_secret=settings.QQ_CLIENT_SECRET,
                           redirect_uri=settings.QQ_REDIRECT_URI,
                           state='/')

        access_token = oauth_qq.get_access_token(code)

        # 获取open_id
        open_id = oauth_qq.get_open_id(access_token)

        # 通过openid查询qq用户
        try:
            qq_user = OAuthQQUser.objects.get(open_id=open_id)
        except Exception as e:
            # qq用户首次登录美多
            encrypt_open_id = encode_openid(open_id)
            context = {
                "token": encrypt_open_id
            }
            # 返回用户授权页面，绑定美多用户
            return render(request, "oauth_callback.html", context=context)
        else:
            # 非首次qq登录用户
            user = qq_user.user
            login(request, user)

            response = redirect('/')

            response.set_cookie("username", user.username)
            response = merge_cookie_redis_data(request, user, response)
            return response

    def post(self, request):
        # 1,获取参数
        encry_openid = request.POST.get("access_token")
        mobile = request.POST.get("mobile")
        password = request.POST.get("pwd")
        sms_code = request.POST.get("sms_code")

        # 2,校验参数
        # 2,0解密openid
        openid = decode_openid(encry_openid)

        if not openid:
            return http.HttpResponseForbidden("openid过期")

        # 2,1为空校验
        if not all([encry_openid, mobile, password, sms_code]):
            return http.HttpResponseForbidden("参数不全")

        # 2,2校验短信验证码
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s" % mobile)

        # 2,3判断短信验证码是否过期
        if not redis_sms_code:
            return http.HttpResponseForbidden("短信过期")

        # 2,4判断正确性
        if sms_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信错误")

        # 3,数据入库
        # 3,1判断账号密码正确性
        user = authenticate(request, username=mobile, password=password)

        # 3,2判断用户是否存在
        if user:
            # 3,3,创建qq用户对象
            qq_user = OAuthQQUser()

            # 3,4 绑定美多用户和openid
            qq_user.user = user
            qq_user.open_id = openid
            qq_user.save()

            # 3,5状态保持
            login(request, user)

            # 3,6返回响应
            response = redirect("/")
            response.set_cookie("username", user.username)
            response = merge_cookie_redis_data(request, user, response)
            return response
        else:
            # 4,1创建美多用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)

            # 4,2创建qq用户,并绑定
            qq_user = OAuthQQUser.objects.create(user=user, open_id=openid)

            # 4,3状态保持
            login(request, user)

            # 4,4 返回响应
            response = redirect("/")
            response.set_cookie("username", user.username)
            response = merge_cookie_redis_data(request, user, response)
            return response


# 获取微博登录页面
class WeiBoLoginView(View):
    def get(self, request):
        client = sinaweibopy3.APIClient(app_key=settings.APP_KEY,
                                        app_secret=settings.APP_SECRET,
                                        redirect_uri=settings.WEIBO_REDIRECT_URI)
        login_url = client.get_authorize_url()
        return http.JsonResponse({
            "login_url": login_url
        })


class WeiBoCallBackView(View):
    def get(self, request):
        client = sinaweibopy3.APIClient(app_key=settings.APP_KEY,
                                        app_secret=settings.APP_SECRET,
                                        redirect_uri=settings.WEIBO_REDIRECT_URI)
        # 获取code
        code = request.GET.get("code")
        if not code:
            return http.HttpResponseForbidden("code丢失")

        # 获取access_token
        result = client.request_access_token(code=code)
        access_token = result.access_token
        uid = request.uid

        # 查询微博用户是否存在
        try:
            weibo_user = OAuthSinaUser.objects.get(uid=uid)
        except Exception as e:
            # weibo用户首次登录美多商城
            encrypt_open_id = encode_openid(uid)
            context = {
                "token": encrypt_open_id
            }
            # 返回用户授权页面，绑定美多用户
            return render(request, "sina_callback.html", context=context)
        else:
            user = weibo_user.user
            login(request, user)

            response = redirect('/')

            response.set_cookie("username", user.username)
            response = merge_cookie_redis_data(request, user, response)
            return response

    def post(self, request):
        # 获取参数
        data_json = request.body.decode()
        data_dict = json.loads(data_json)
        password = data_dict.get("password")
        mobile = data_dict.get("mobile")
        sms_code = data_dict.get("sms_code")
        access_token = data_dict.get("access_token")

        # 校验参数
        # 为空校验
        if not all([password, mobile, sms_code, access_token]):
            return http.HttpResponseForbidden("参数不全")

        # 校验密码、手机号码是否符合规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden("密码格式有误")

        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden("手机号码格式有误")

        # 校验短信验证码
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s" % mobile)

        # 判断短信验证码是否过期
        if not redis_sms_code:
            return http.HttpResponseForbidden("短信过期")

        # 校验短信验证码是否正确
        if sms_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信错误")

        # 校验access_token是否正确
        uid = decode_openid(access_token)

        # 判断用户是否存在及入库
        user = authenticate(request, username=mobile, password=password)

        if user:
            # 创建微博用户对象
            weibo_user = OAuthSinaUser()

            weibo_user.user = user
            weibo_user.uid = uid
            weibo_user.save()

        else:
            # 创建美多用户
            user = User.objects.create_user(username=mobile,
                                            password=password,
                                            mobile=mobile)
            # 绑定微博用户
            weibo_user = OAuthSinaUser.objects.create(user=user, uid=uid)

        login(request, user)
        # 返回响应
        response = redirect('/')
        response.set_cookie("username", user.username)
        response = merge_cookie_redis_data(request, user, response)
        return response


class SinaUserView(View):
    def post(self, request):
        # 获取参数
        data_json = request.body.decode()
        data_dict = json.loads(data_json)
        password = data_dict.get("password")
        mobile = data_dict.get("mobile")
        sms_code = data_dict.get("sms_code")
        access_token = data_dict.get("access_token")

        # 校验参数
        # 为空校验
        if not all([password, mobile, sms_code, access_token]):
            return http.HttpResponseForbidden("参数不全")

        # 校验密码、手机号码是否符合规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden("密码格式有误")

        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden("手机号码格式有误")

        # 校验短信验证码
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s" % mobile)

        # 判断短信验证码是否过期
        if not redis_sms_code:
            return http.HttpResponseForbidden("短信过期")

        # 校验短信验证码是否正确
        if sms_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信错误")

        # 校验access_token是否正确
        uid = decode_openid(access_token)

        # 判断用户是否存在及入库
        user = authenticate(request, username=mobile, password=password)

        if user:
            # 创建微博用户对象
            weibo_user = OAuthSinaUser()

            weibo_user.user = user
            weibo_user.uid = uid
            weibo_user.save()

        else:
            # 创建美多用户
            user = User.objects.create_user(username=mobile,
                                            password=password,
                                            mobile=mobile)
            # 绑定微博用户
            weibo_user = OAuthSinaUser.objects.create(user=user, uid=uid)

        # 返回响应
        return http.JsonResponse({
            "user_id": user.id,
            "username": user.username,
        })

