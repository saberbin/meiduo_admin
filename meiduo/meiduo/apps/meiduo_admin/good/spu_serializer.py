from rest_framework import serializers
from goods.models import SPU, SPUSpecification, SpecificationOption, SKUSpecification
from goods.models import Brand, GoodsCategory


class SPUSerializer(serializers.ModelSerializer):
    # 重写brand
    brand = serializers.StringRelatedField(read_only=True)
    brand_id = serializers.IntegerField()
    # 重写分类
    category1 = serializers.StringRelatedField(read_only=True)
    category1_id = serializers.IntegerField()

    category2 = serializers.StringRelatedField(read_only=True)
    category2_id = serializers.IntegerField()

    category3 = serializers.StringRelatedField(read_only=True)
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        fields = "__all__"


# spu品牌序列化器
class SPUBrandSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name")


# spu, category序列化器
class SPUCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ("id", "name")



