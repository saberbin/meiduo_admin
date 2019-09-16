from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from goods.models import GoodsChannel, GoodsCategory, GoodsChannelGroup
from meiduo_admin.my_paginate import MyPageNumberPagination
from meiduo_admin.good import channels_serializer
from meiduo_admin.good import spu_serializer


class ChannelsViewSet(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = channels_serializer.ChannelsSerializer
    queryset = GoodsChannel.objects.order_by("id").all()


# 频道管理新增获取一级分类选项　ChannelsCatrgoryView
class ChannelsCatrgoryView(ListAPIView):
    serializer_class = spu_serializer.SPUCategorySerializer
    queryset = GoodsCategory.objects.filter(parent__isnull=True).all()


# 频道管理新增获取频道组
class ChannelsTypeView(ListAPIView):
    serializer_class = channels_serializer.ChannelsTypeSerializer
    queryset = GoodsChannelGroup.objects.all()


