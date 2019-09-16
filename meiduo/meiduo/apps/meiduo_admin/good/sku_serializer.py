from rest_framework import serializers
from goods.models import SKU, GoodsCategory, SKUSpecification
from goods.models import SPU, SpecificationOption, SPUSpecification
from django.db import transaction


# 规格选项序列化器
class SKUSpecificationSerializer(serializers.Serializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()


# SKU序列化器
class SKUSerializer(serializers.ModelSerializer):
    # spu\spu_id
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    # category,category_id
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()

    # 匹配规格选项
    specs = SKUSpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        sid = transaction.savepoint()  # set the save point
        try:
            sku = SKU.objects.create(**validated_data)

            specs = self.context["request"].data["specs"]
            for spec_dict in specs:
                SKUSpecification.objects.create(sku_id=sku.id,
                                                spec_id=spec_dict["spec_id"],
                                                option_id=spec_dict["option_id"])
        except Exception as e:
            transaction.savepoint_rollback(sid)  # 保存点回滚
            raise serializers.ValidationError("sku保存失败")
        else:
            transaction.savepoint_commit(sid)  # 保存点提交
            return sku

    @transaction.atomic
    def update(self, instance, validated_data):
        sid = transaction.savepoint()  # set the save point
        try:
            SKU.objects.filter(id=instance.id).update(**validated_data)
            [spec.delete() for spec in instance.specs.all()]
            specs = self.context["request"].data["specs"]
            for spec_dict in specs:
                SKUSpecification.objects.create(sku_id=instance.id,
                                                spec_id=spec_dict["spec_id"],
                                                option_id=spec_dict["option_id"])
        except Exception as e:
            transaction.savepoint_rollback(sid)
            raise serializers.ValidationError("sku数据更新错误")
        else:
            transaction.savepoint_commit(sid)
            return SKU.objects.get(id=instance.id)


class SKUCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class SKUSPUSimpleView(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = ("id", "name")


# 选项序列化器
class SPUSpecificationOption(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ("id", "value")


# spu specification option 序列化器
class SPUSpecificationSerializer(serializers.ModelSerializer):
    options = SPUSpecificationOption(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = "__all__"

