from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from goods.models import GoodsChannel, GoodsCategory, GoodsChannelGroup, Brand
from meiduo_admin.my_paginate import MyPageNumberPagination
from meiduo_admin.good import brands_serializers


# 品牌管理视图集
class BrandsViewSet(ModelViewSet):
    serializer_class = brands_serializers.BrandsSerializer
    queryset = Brand.objects.order_by("id").all()
    pagination_class = MyPageNumberPagination


