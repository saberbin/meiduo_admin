from rest_framework.viewsets import ModelViewSet
from meiduo_admin.good import spu_specs_serializers
from goods.models import SPUSpecification, SpecificationOption
from meiduo_admin.my_paginate import MyPageNumberPagination
from rest_framework.generics import ListAPIView


# spu spces
class SPUSpecViewSet(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = spu_specs_serializers.SPUSpecsSerializer
    queryset = SPUSpecification.objects.order_by("id").all()


# specs options
class SPecsOptionViewSet(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = spu_specs_serializers.SPecsOptionSerializer
    queryset = SpecificationOption.objects.order_by("id").all()


# spec信息获取
class SpecsSimpleView(ListAPIView):
    serializer_class = spu_specs_serializers.SpecsSimpleSerializer

    def get_queryset(self):
        queryset = SPUSpecification.objects.all()

        # 给数据源name增加spu.name属性
        for spec in queryset:
            spec.name = "%s - %s" % (spec.spu.name, spec.name)

        # 返回数据源
        return queryset

