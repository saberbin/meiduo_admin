from django.shortcuts import render, redirect
from django.views import View
from meiduo.utils.my_category import get_categories
from goods.models import SKU, GoodsCategory, CategoryVisitCount
from django.core.paginator import Paginator
from meiduo.utils import my_constants
from django.conf import settings
from django import http
from meiduo.utils.response_code import RETCODE
from datetime import datetime
from meiduo.utils.my_loginrequired import MyLoginRequiredMixin
import json
from django_redis import get_redis_connection


# 商品列表页面
class SKUListView(View):
    def get(self, request, category_id, page_num):
        categories = get_categories()

        # 获取参数
        sort = request.GET.get("sort", "default")
        if sort == "price":
            sort_field = "price"
        elif sort == "hot":
            sort_field = "sales"
        else:
            sort_field = "-create_time"

        skus = SKU.objects.filter(category_id=category_id).order_by(sort_field).all()
        # 查询分类数据
        category = GoodsCategory.objects.get(id=category_id)

        # 对数据进行分页
        paginate = Paginator(skus, my_constants.LIST_SKU_PER_COUNT)
        page = paginate.page(page_num)
        current_page = page.number  # 当前页
        sku_list = page.object_list  # 当前页对象
        total_page = paginate.num_pages

        context = {
            "categories": categories,
            "skus": sku_list,
            "category": category,
            "current_page": current_page,
            "total_page": total_page,
            "sort": sort
        }
        return render(request, 'list.html', context=context)


# 商品热销排行
class HotSKUListView(View):
    def get(self, request, category_id):
        # 1. 查询热销的商品数据
        skus = SKU.objects.filter(category_id=category_id).order_by("-sales")[:2]
        # 进行数据转换
        sku_list = []
        for sku in skus:
            sku_dict = {
                "id": sku.id,
                "default_image_url": sku.default_image_url.url,
                "name": sku.name,
                "price": sku.price
            }
            sku_list.append(sku_dict)

        return http.JsonResponse({
            "code": RETCODE.OK,
            "hot_sku_list": sku_list
        })


# 商品详情页面展示
class SKUDetailView(View):
    def get(self, request, sku_id):

        # 1,获取分类数据
        categories = get_categories()

        # 2,获取面包屑数据
        sku = SKU.objects.get(id=sku_id)
        category = sku.category

        # 3,规格信息数据
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 拼接数据,渲染页面
        context = {
            "categories": categories,
            "category": category,
            "sku": sku,
            "specs": goods_specs
        }
        return render(request, 'detail.html', context=context)

        # 4,记录分类访问量


class CategoryVisitCountView(View):
    def post(self, request, category_id):

        # 0,获取当天时间
        today = datetime.today()

        # 1,查询访问量对象
        try:
            category_visit = CategoryVisitCount.objects.get(date=today, category_id=category_id)
        except Exception as e:
            category_visit = CategoryVisitCount()

        # 2,数据入库
        category_visit.date = today
        category_visit.category_id = category_id
        category_visit.count += 1
        category_visit.save()

        # 3,返回响应
        return http.JsonResponse({"code": RETCODE.OK}, status=200)


# 记录商品浏览历史
class SKUBrowseHistoryView(MyLoginRequiredMixin):
    def post(self, request):
        dict_data = json.loads(request.body.decode())
        sku_id = dict_data.get("sku_id")
        user = request.user

        if not sku_id:
            return http.JsonResponse({"code": RETCODE.NODATAERR, "errmsg": "参数不全"})

        redis_conn = get_redis_connection("history")
        redis_conn.lrem("history_%s" % user.id, 0, sku_id)  # 去除重复数据
        redis_conn.lpush("history_%s" % user.id, sku_id)

        redis_conn.ltrim("history_%s" % user.id, 0, 4)
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "操作成功"})

    def get(self, request):
        # 获取浏览历史记录
        redis_conn = get_redis_connection("history")
        sku_ids = redis_conn.lrange("history_%s" % request.user.id, 0, 4)

        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_dict = {
                "id": sku.id,
                "default_image_url": sku.default_image_url.url,
                "name": sku.name,
                "price": sku.price
            }
            sku_list.append(sku_dict)

        return http.JsonResponse({"code": RETCODE.OK, "skus": sku_list})



