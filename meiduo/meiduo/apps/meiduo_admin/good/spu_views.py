from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
# from fdfs_client.client import Fdfs_client  # has remove the fdfs-client-py
from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.my_paginate import MyPageNumberPagination
from meiduo_admin.good import spu_serializer
from goods.models import SPU, SPUSpecification, SKUSpecification, Brand
from goods.models import GoodsCategory


# spu商品图片上传
# class SPUImageUploadView(APIView):
#     def post(self, request):
#         # get the image data from request
#         image = request.FILES.get("image")
#         # check the image is empty or not
#         if not image:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#
#         client = Fdfs_client(settings.BASE_CONFIG)
#         result = client.upload_by_buffer(image.read())
#
#         if result.get("status") != "upload sucessed.":
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#
#         image_url = result.get("Remoto file_id")
#
#         # return response
#         return Response({
#             "img_url": "%s%s" % (settings.BASE_URL, image_url)
#         })


# spu管理
class SPUViewSet(ModelViewSet):
    serializer_class = spu_serializer.SPUSerializer
    queryset = SPU.objects.order_by("id").all()
    pagination_class = MyPageNumberPagination


# spu brand品牌获取
class SPUBrandSimpleView(ListAPIView):
    serializer_class = spu_serializer.SPUBrandSimpleSerializer
    queryset = Brand.objects.all()


# spu category一级分类获取
class SPUCategoryView(ListAPIView):
    serializer_class = spu_serializer.SPUCategorySerializer
    queryset = GoodsCategory.objects.filter(parent__isnull=True)


# spu category二、三级分类获取
class SPUSubsCategoryView(ListAPIView):
    serializer_class = spu_serializer.SPUCategorySerializer

    def get_queryset(self):
        catrgory_id = self.kwargs.get("category_id")
        queryset = GoodsCategory.objects.filter(parent_id=catrgory_id).all()
        return queryset



