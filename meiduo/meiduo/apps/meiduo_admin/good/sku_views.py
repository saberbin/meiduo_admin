from rest_framework.viewsets import ModelViewSet
from meiduo_admin.my_paginate import MyPageNumberPagination
from . import sku_serializer
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification
from rest_framework.generics import ListAPIView


# sku管理
class SKUViewSet(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = sku_serializer.SKUSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get("keyword")

        if keyword:
            return SKU.objects.filter(name__contains=keyword).all()
        else:
            return SKU.objects.order_by("id").all()


class SKUCategoryView(ListAPIView):
    serializer_class = sku_serializer.SKUCategorySerializer
    queryset = GoodsCategory.objects.filter(subs__isnull=True).all()


class SKUSPUSimpleView(ListAPIView):
    serializer_class = sku_serializer.SKUSPUSimpleView
    queryset = SPU.objects.all()


#
class SPUSpecificationView(ListAPIView):
    serializer_class = sku_serializer.SPUSpecificationSerializer

    def get_queryset(self):
        spu_id = self.kwargs.get("spu_id")
        return SPUSpecification.objects.filter(spu_id=spu_id).all()

