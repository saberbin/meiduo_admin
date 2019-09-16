from rest_framework import serializers
from goods.models import SKUImage, SKU


# sku image序列化器
class SKUImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = "__all__"


# image sku list simple
class SKUImageSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ("id", "name")
