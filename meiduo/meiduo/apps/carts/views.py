from django.shortcuts import render
from django.views import View
from django import http
import json
from meiduo.utils.response_code import RETCODE
from goods.models import SKU
from django_redis import get_redis_connection
import pickle
import base64


# Create your views here.
class CartView(View):
    def post(self, request):
        """添加购物车"""
        # 1. get the data
        dict_data = json.loads(request.body.decode())
        sku_id = dict_data.get("sku_id")
        count = dict_data.get("count")
        selected = dict_data.get("selected", True)

        # check the data
        if not all([sku_id, count]):
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "参数不全"})

        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "找不到商品"})

        # 检查ｃｏｕｎｔ是否为整数
        try:
            count = int(count)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "count不是整数"})

        # 检查库存是否足够
        if count > sku.stock:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "库存不够"})

        user = request.user
        if request.user.is_authenticated:
            # 认证用户
            redis_conn = get_redis_connection("carts")

            # save the sku to the redis
            redis_conn.hincrby("carts_%s" % user.id, sku_id, count)

            # 判断商品是否被勾选
            if selected:
                redis_conn.sadd("selected_%s" % user.id, sku_id)

            return http.JsonResponse({"code": RETCODE.OK})
        else:
            # 非认证用户
            # 获取ｃｏｏｋｉｅｓ购物车数据
            cart_cookie = request.COOKIES.get("cart")

            # save the cart_cookie as dict data
            cart_cookie_dict = {}
            if cart_cookie:
                cart_cookie_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))

            # 如果添d加的商品在购物车中已存在，则增加计数
            if sku_id in cart_cookie_dict:
                old_count = cart_cookie_dict[sku_id]["count"]
                count += old_count

            # 添加新的数据到字典中
            cart_cookie_dict[sku_id] = {
                "count": count,
                "selected": selected
            }

            response = http.JsonResponse({"code": RETCODE.OK})
            cart_cookie = base64.b64encode(pickle.dumps(cart_cookie_dict)).decode()
            response.set_cookie("cart", cart_cookie)
            return response

    def get(self, request):
        # １．判断用户是否已登录
        user = request.user
        if request.user.is_authenticated:
            redis_conn = get_redis_connection("carts")
            cart_dict = redis_conn.hgetall("carts_%s" % user.id)
            selected_list = redis_conn.smembers("selected_%s" % user.id)

            sku_list = []
            for sku_id in cart_dict.keys():
                sku = SKU.objects.get(id=sku_id)
                sku_dict = {
                    "id": sku.id,
                    "default_image_url": sku.default_image_url.url,
                    "name": sku.name,
                    "selected": str(sku_id in selected_list),
                    "price": str(sku.price),
                    "count": int(cart_dict[sku_id]),
                    "amount": str(int(cart_dict[sku_id]) * sku.price)
                }
                sku_list.append(sku_dict)

            return render(request, "cart.html", context={"sku_list": sku_list})
        else:
            # get the cart data from cookies
            cart_cookie = request.COOKIES.get("cart")
            # change the cart_cookie to the cart_cookie dict data
            cart_cookie_dict = {}
            if cart_cookie:
                cart_cookie_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
            sku_list = []
            for sku_id, selected_count in cart_cookie_dict.items():
                sku = SKU.objects.get(id=sku_id)
                sku_dict = {
                    "id": sku.id,
                    "default_image_url": sku.default_image_url.url,
                    "name": sku.name,
                    "selected": str(selected_count["selected"]),
                    "price": str(sku.price),
                    "count": int(selected_count["count"]),
                    "amount": str(int(selected_count["count"]) * sku.price)
                }
                sku_list.append(sku_dict)

            return render(request, "cart.html", context={"sku_list": sku_list})

    def put(self, request):
        dict_data = json.loads(request.body.decode())
        sku_id = dict_data.get("sku_id")
        count = dict_data.get("count")
        selected = dict_data.get("selected", True)

        # check the data
        if not all([sku_id, count, selected]):
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "参数不全"})

        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "商品不存在"})

        # 检查ｃｏｕｎｔ是否为整数
        try:
            count = int(count)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "count不是整数"})

        # 检查库存是否足够
        if count > sku.stock:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "库存不够"})

        # save the data to the database
        user = request.user
        if request.user.is_authenticated:
            # get the redis connect
            redis_conn = get_redis_connection("carts")
            redis_conn.hset("carts_%s" % user.id, sku_id, count)
            if selected:
                redis_conn.sadd("selected_%s" % user.id, sku_id)
            else:
                redis_conn.srem("selected_%s" % user.id, sku_id)
            sku = SKU.objects.get(id=sku_id)
            sku_dict = {
                "id": sku.id,
                "default_image_url": sku.default_image_url.url,
                "name": sku.name,
                "selected": selected,
                "price": str(sku.price),
                "count": int(count),
                "amount": str(int(count) * sku.price)
            }
            return http.JsonResponse({"code": RETCODE.OK, "cart_sku": sku_dict})
        else:
            cart_cookie = request.COOKIES.get("cart")
            cart_cookie_dict = {}
            if cart_cookie:
                cart_cookie_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))

            cart_cookie_dict[sku_id] = {
                "selected": selected,
                "count": count
            }

            sku = SKU.objects.get(id=sku_id)
            sku_dict = {
                "id": sku_id,
                "default_image_url": sku.default_image_url.url,
                "name": sku.name,
                "selected": selected,
                "price": str(sku.price),
                "count": int(count),
                "amount": str(int(count) * sku.price)
            }

            response = http.JsonResponse({"code": RETCODE.OK, "cart_sku": sku_dict})
            cart_cookie = base64.b64encode(pickle.dumps(cart_cookie_dict)).decode()
            response.set_cookie("cart", cart_cookie)
            return response

    def delete(self, request):
        dict_data = json.loads(request.body.decode())
        sku_id = dict_data.get("sku_id")

        if not sku_id:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "参数不全"})

        # 删除数据
        user = request.user
        if request.user.is_authenticated:
            redis_conn = get_redis_connection("carts")
            redis_conn.hdel("carts_%s" % user.id, sku_id)
            redis_conn.srem("selected_%s" % user.id, sku_id)
            return http.JsonResponse({"code": RETCODE.OK})
        else:
            cart_cookie = request.COOKIES.get("cart")
            cart_cookie_dict = {}
            if cart_cookie:
                cart_cookie_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))

            if sku_id in cart_cookie_dict:
                del cart_cookie_dict[sku_id]

            response = http.JsonResponse({"code": RETCODE.OK})
            cart_cookie = base64.b64encode(pickle.dumps(cart_cookie_dict)).decode()
            response.set_cookie("cart", cart_cookie)
            return response


# 全选购物车
class CartSelectedAllView(View):
    def put(self, request):
        dict_data = json.loads(request.body.decode())
        selected = dict_data.get("selected", True)

        try:
            selected = bool(selected)
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "参数类型有误"})
        user = request.user
        if request.user.is_authenticated:
            # get the redis connect
            redis_conn = get_redis_connection("carts")
            cart_dict = redis_conn.hgetall("carts_%s" % user.id)
            sku_ids = cart_dict.keys()
            if selected:
                redis_conn.sadd("selected_%s" % user.id, *sku_ids)
            else:
                redis_conn.srem("selected_%s" % user.id, *sku_ids)
                return http.JsonResponse({"code": RETCODE.OK})
        else:
            cart_cookie = request.COOKIES.get("cart")
            cart_cookie_dict = {}
            if cart_cookie:
                cart_cookie_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
            for sku_id, selected_count in cart_cookie_dict.items():
                selected_count["selected"] = selected

            response = http.JsonResponse({"code": RETCODE.OK})
            cart_cookie = base64.b64encode(pickle.dumps(cart_cookie_dict)).decode()
            response.set_cookie("cart", cart_cookie)
            return response


# 简要购物车界面展示
class CartSimpleView(View):
    def get(self, request):
        # 判断是否登录用户
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection("carts")
            cart_dict = redis_conn.hgetall("carts_%s" % user.id)
            selected_list = redis_conn.smembers("selected_%s" % user.id)

            sku_list = []
            for sku_id in cart_dict.keys():
                sku = SKU.objects.get(id=sku_id)
                sku_dict = {
                    "id": sku.id,
                    "default_image_url": sku.default_image_url.url,
                    "name": sku.name,
                    "count": int(cart_dict[sku_id]),
                }
                sku_list.append(sku_dict)

            return http.JsonResponse({"cart_skus": sku_list})
        else:
            # get the cart data from cookies
            cart_cookie = request.COOKIES.get("cart")
            # change the cart_cookie to the cart_cookie dict data
            cart_cookie_dict = {}
            if cart_cookie:
                cart_cookie_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
            sku_list = []
            for sku_id, selected_count in cart_cookie_dict.items():
                sku = SKU.objects.get(id=sku_id)
                sku_dict = {
                    "id": sku.id,
                    "default_image_url": sku.default_image_url.url,
                    "name": sku.name,
                    "count": int(selected_count["count"]),
                }
                sku_list.append(sku_dict)
            return http.JsonResponse({"cart_skus": sku_list})

