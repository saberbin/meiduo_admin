from django.shortcuts import render, redirect
from users.models import User, Address
from django.views import View
from django import http
import re
import json
from django_redis import get_redis_connection
from django.contrib.auth import authenticate, login, logout
from meiduo.utils import my_constants
from carts.utils import merge_cookie_redis_data
from meiduo.utils.my_openid import decode_openid, encode_openid
from meiduo.utils.my_loginrequired import MyLoginRequiredMixin
from meiduo.utils.response_code import RETCODE
from meiduo.utils.my_email import generate_verify_url, decode_token
from django.core.mail import send_mail
from django.conf import settings
from areas.models import Area


# 用户注册界面
class UserRegisterView(View):
    def get(self, request):
        # 返回用户注册页面
        return render(request, 'register.html')

    def post(self, request):
        # 获取参数
        username = request.POST.get("user_name")
        pwd = request.POST.get("pwd")
        cpwd = request.POST.get("cpwd")
        mobile = request.POST.get("phone")
        # pic_code = request.POST.get("pic_code")
        msg_code = request.POST.get("msg_code")
        allow = request.POST.get("allow")

        # 检查参数
        # 2.1 检查参数是否为空值
        if not all([username, pwd, cpwd, mobile, msg_code]):
            return http.HttpResponseForbidden("参数不全")

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("用户名格式有误")

        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden("密码格式有误")

        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden("手机号码格式有误")

        if pwd != cpwd:
            return http.HttpResponseForbidden("两次密码不一致")

        if allow != 'on':
            return http.HttpResponseForbidden("必须同意用户协议")

        # 校验短信验证码
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s" % mobile)

        # 判断短信验证码是否存在，若不存在则已过期
        if not redis_sms_code:
            return http.HttpResponseForbidden("短信验证码已过期，请重试")

        # 判断短信验证码是否正确
        if redis_sms_code.decode() != msg_code:
            return http.HttpResponseForbidden("短信验证码错误")

        # 创建用户
        user = User.objects.create_user(username=username, password=pwd, mobile=mobile)

        return redirect('/')


# 检查用户名是否已存在
class UsernameCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        return http.JsonResponse({"count": count})


# 检查手机号码是否已存在
class UserPhoneCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return http.JsonResponse({"count": count})


# 用户登录
class UserLoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 获取参数
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        remembered = request.POST.get("remembered")

        # 检验参数
        # 检查参数是否为空
        if not all([username, password, remembered]):
            return http.HttpResponseForbidden("参数不全，请重试")

        # 检查用户名、密码是否符合规则
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("用户名格式有误")

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden("密码格式有误")

        # 检查用户名在数据库中是否存在
        count = User.objects.filter(username=username).count()
        if count == 0:
            return http.HttpResponseForbidden("用户名不存在")

        # 检查用户密码是否正确
        user = authenticate(request, username=username, password=password)
        if not user:
            return http.HttpResponseForbidden("用户不存在")

        # 用户登录
        login(request, user)

        response = redirect('/')

        # 是否记住密码
        if remembered == "on":
            request.session.set_expiry(my_constants.SESSIOIN_MAX_AGE)
            response.set_cookie("username", user.username, my_constants.SESSIOIN_MAX_AGE)
        else:
            response.set_cookie("username", user.username)

        # 返回响应
        response = merge_cookie_redis_data(request, user, response)
        return response


# 用户登出
class UserLogoutView(View):
    def get(self, request):
        response = redirect('/')
        response.delete_cookie("username")

        # 登出用户
        logout(request)

        return response


# 用户找回密码界面
class UserFPView(View):
    def get(self, request):
        return render(request, "find_password.html")


# 找回密码的密码验证及保存
class UserFPChangePasswordView(View):
    def post(self, request, user_id):
        # 获取参数
        data = request.body.decode()
        data_dict = json.loads(data)
        password = data_dict.get("password")
        password2 = data_dict.get("password2")
        access_token = data_dict.get("access_token")

        if not all([user_id, password, password2, access_token]):
            return http.JsonResponse({"message": "参数不全"})

        # 校验两次密码是否一致
        if password != password2:
            return http.JsonResponse({"message": "两次密码不一致"})

        # 检查用户是否存在
        try:
            user = User.objects.get(id=user_id)
        except Exception as e:
            return http.JsonResponse({"message": "用户不存在"})

        # 校验access_token是否正确
        token = decode_openid(access_token)
        if token != user.username:
            return http.JsonResponse({"message": "token被修改了，请重试"})

        # 检查新密码是否跟旧密码一致
        if user.check_password(password):
            return http.JsonResponse({"message": "新密码不能与旧密码一致"})

        # 设置新密码保存到数据库
        user.set_password(password)
        user.save()

        # 返回响应
        return http.JsonResponse({"message": "修改密码成功，请重新登陆"}, status=200)


# 显示用户中心
class UserInfoView(MyLoginRequiredMixin):
    def get(self, request):
        user = request.user
        context = {
            "username": user.username,
            "mobile": user.mobile,
            "email": user.email,
            "email_active": user.email_active
        }

        return render(request, "user_center_info.html", context=context)


# 用户验证邮件发送
class UsereEmailsView(MyLoginRequiredMixin):
    def put(self, request):
        # 获取参数
        data_json = request.body.decode()
        data_dict = json.loads(data_json)
        email = data_dict.get("email")

        # 校验参数
        if not email:
            return http.JsonResponse({"code": RETCODE.NODATAERR,
                                      "errmsg": "参数不全"})

        verify_url = generate_verify_url(user=request.user)
        email_msg = "<h3>美多商城邮箱激活邮件，请点击下面的链接进行激活，如非本人操作请忽视</h3>" \
                    "<a href='%s'>点击激活链接激活</a>" % verify_url
        # setting the sending settings
        # send_mail(subject="美多商城激活链接",  message=email_msg, from_email=settings.EMAIL_FROM,
        #           recipient_list=[email])
        send_mail(subject="美多商城激活链接", html_message=email_msg, from_email=settings.EMAIL_FROM,
                  recipient_list=[email])
        # send_mail(subject="美多商城激活链接", message=verify_url, from_email=settings.EMAIL_FROM, recipient_list=[email])

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "验证邮件发送成功"})


# 用户邮箱激活
class UserEmailVerificationView(View):
    def get(self, request):
        # 获取参数
        token = request.GET.get("token")

        if not token:
            return http.HttpResponseForbidden("token丢失")

        user = decode_token(token)

        if not user:
            return http.HttpResponseForbidden("token失效了，请重发邮件")

        user.email_active = True
        user.save()

        return http.HttpResponse("邮箱激活成功！")


# 渲染用户收货地址页面
class UserAddressView(MyLoginRequiredMixin):
    def get(self,request):
        #1,获取数据
        # Address.objects.filter(user_id=request.user.id).all()
        addresses = request.user.addresses.filter(is_deleted=False).all()

        #2,拼接数据
        address_list = []
        for address in addresses:
            address_dict = {
                "id":address.id,
                "receiver":address.receiver,
                "province":address.province.name,
                "city":address.city.name,
                "district":address.district.name,
                "place":address.place,
                "mobile":address.mobile,
                "tel":address.tel,
                "email":address.email,
                "province_id":address.province_id,
                "city_id":address.city_id,
                "district_id":address.district_id,
            }
            address_list.append(address_dict)

        #3,渲染页面
        context = {
            "addresses":address_list,
            "user":request.user
        }
        return render(request,'user_center_site.html',context=context)


# 新增用户收货地址
class UserAddressCreateView(MyLoginRequiredMixin):
    def post(self, request):
        # 1,获取参数
        dict_data = json.loads(request.body.decode())
        title = dict_data.get("title")
        receiver = dict_data.get("receiver")
        province_id = dict_data.get("province_id")
        city_id = dict_data.get("city_id")
        district_id = dict_data.get("district_id")
        place = dict_data.get("place")
        mobile = dict_data.get("mobile")
        tel = dict_data.get("tel")
        email = dict_data.get("email")

        # 2,校验参数(为空校验)
        # if not all([title, receiver, province_id, city_id, district_id, place, mobile, tel, email]):
        # 修改校验参数逻辑，非必填字段不需要校验是否存在
        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({"errmsg": "参数不全", "code": RETCODE.NODATAERR})

        # 3,数据入库
        dict_data['user'] = request.user
        address = Address.objects.create(**dict_data)

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "my_email": address.email,
            "province_id": address.province_id,
            "city_id": address.city_id,
            "district_id": address.district_id,
        }

        # 4,返回响应
        context = {
            "code": RETCODE.OK,
            "address": address_dict
        }
        return http.JsonResponse(context)


# 设置用户默认地址
class UserAddressDefaultView(MyLoginRequiredMixin):
    def put(self, request, address_id):
        # 设置默认地址
        request.user.default_address_id = address_id

        # save the data to the database
        request.user.save()
        # return the response
        return http.JsonResponse({"code": RETCODE.OK})


# 修改用户地址
class UserAddressUpdateView(MyLoginRequiredMixin):
    def put(self,request,address_id):
        #1,获取参数
        dict_data = json.loads(request.body.decode())
        title = dict_data.get("title")
        receiver = dict_data.get("receiver")
        province_id = dict_data.get("province_id")
        city_id = dict_data.get("city_id")
        district_id = dict_data.get("district_id")
        place = dict_data.get("place")
        mobile = dict_data.get("mobile")
        tel = dict_data.get("tel")
        email = dict_data.get("email")

        #2,参数校验(为空校验)
        # if not all([title,receiver,province_id,city_id,district_id,place,mobile,tel,email]):
        # 修改校验参数逻辑，非必填字段不需要校验是否存在
        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({"errmsg":"参数不全","code":RETCODE.NODATAERR})

        #3,数据入库
        address = Address.objects.get(id=address_id)
        address.title = title
        address.receiver = receiver
        address.province_id = province_id
        address.city_id = city_id
        address.district_id = district_id
        address.place = place
        address.mobile = mobile
        address.tel = tel
        address.email = email
        address.save()

        #4,返回响应
        address_dict = {
                "id":address.id,
                "title":address.title,
                "receiver":address.receiver,
                "province":address.province.name,
                "city":address.city.name,
                "district":address.district.name,
                "place":address.place,
                "mobile":address.mobile,
                "tel":address.tel,
                "my_email":address.email,
                "province_id":address.province_id,
                "city_id":address.city_id,
                "district_id":address.district_id,
        }

        context = {
            "code":RETCODE.OK,
            "address":address_dict
        }
        return http.JsonResponse(context)

    def delete(self,request,address_id):
        #1,删除地址
        address = Address.objects.get(id=address_id)
        address.is_deleted = True
        address.save()

        #2,返回响应
        return http.JsonResponse({
            "code":RETCODE.OK
        })


# 修改地址标题
class UserAddressTitleView(MyLoginRequiredMixin):
    def put(self,request,address_id):
        #1,获取参数
        dict_data = json.loads(request.body.decode())
        title = dict_data.get("title")

        #2,校验参数
        if not title:
            return http.JsonResponse({"errmsg":"参数不全","code":RETCODE.NODATAERR})

        #3,数据入库
        # address = Address.objects.get(id=address_id)
        # address.title = title
        # address.save()

        Address.objects.filter(id=address_id).update(title=title) #和上面三句话等价

        #4,返回响应
        return http.JsonResponse({
            "code":RETCODE.OK
        })


# 获取密码修改页面
class UserChangePasswordView(MyLoginRequiredMixin):
    def get(self, request):
        return render(request, "user_center_pass.html")

    def post(self, request):
        # get the data from request
        old_pwd = request.POST.get("old_pwd")
        new_pwd = request.POST.get("new_pwd")
        new_cpwd = request.POST.get("new_cpwd")

        # check the data
        # check the data is empty or not
        if not all([old_pwd, new_cpwd, new_pwd]):
            return render(request, "user_center_pass.html")

        # 检查两次新密码是否一致
        if new_cpwd != new_pwd:
            return render(request, "user_center_pass.html")

        if old_pwd == new_cpwd:
            return render(request, "user_center_pass.html")

        # 数据入库
        request.user.set_password(new_pwd)
        request.user.save()

        # 返回响应，重定向到首页
        return redirect('/')



