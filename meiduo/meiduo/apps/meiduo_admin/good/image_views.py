from rest_framework.viewsets import ModelViewSet
from meiduo_admin.good import image_serializers
from rest_framework.response import Response
from meiduo_admin.my_paginate import MyPageNumberPagination
from rest_framework.generics import ListAPIView
from goods.models import SKUImage, SKU
from rest_framework import status
from django.conf import settings


# image管理视图集
class SKUImagesViewSet(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = image_serializers.SKUImagesSerializer
    queryset = SKUImage.objects.order_by("id").all()

    # overwrite the create function to save the image to fdfs and save the image url to the database
    # def create(self, request, *args, **kwargs):
    #     # get the data from request
    #     sku_id = request.data.get("sku")
    #     image = request.FILES.get("image")
    #
    #     # check the data is empty or not
    #     if not all([sku_id, image]):
    #         return Response(status=400)
    #
    #     client = Fdfs_client(settings.BASE_CONFIG)
    #     result = client.upload_by_buffer(image.read())
    #
    #     if result.get("status") != "upload sucessed.":
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #
    #     image_url = result.get("Remoto file_id")
    #
    #     # save the image to the database
    #     SKUImage.objects.create(image=image_url, sku_id=sku_id)
    #     SKU.objects.filter(id=sku_id, default_image_url="").update(default_image_url=image_url)
    #
    #     # return response
    #     return Response(status=200)

    # overwrite the update function to update the sku image in fdfs and the database
    # def update(self, request, *args, **kwargs):
    #     # get the data from request
    #     sku_id = request.data.get("sku")
    #     image = request.FILES.get("image")
    #     sku_image = self.get_object()
    #
    #     # check the data is empty or not
    #     if not all([sku_id, image]):
    #         return Response(status=400)
    #
    #     # upload the image
    #     client = Fdfs_client(settings.BASE_CONFIG)
    #     result = client.upload_by_buffer(image.read())
    #
    #     if result.get("status") != "upload sucessed.":
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #
    #     image_url = result.get("Remoto file_id")
    #     # save the image to the database
    #     SKUImage.objects.filter(id=sku_image.id).update(image=image_url, sku_id=sku_id)
    #     return Response(status=status.HTTP_201_CREATED)


# image
class SKUImageSimpleView(ListAPIView):
    serializer_class = image_serializers.SKUImageSimpleSerializer
    queryset = SKU.objects.all()


