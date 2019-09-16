from rest_framework import serializers
from goods.models import Brand
from django.db import transaction


# 品牌视图集
class BrandsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = "__all__"

    # 重写更新数据的方法
    @transaction.atomic
    def update(self, instance, validated_data):
        sid = transaction.savepoint()
        try:
            Brand.objects.filter(id=instance.id).update(**validated_data)
        except Exception as e:
            transaction.savepoint_rollback(sid)
            raise serializers.ValidationError("品牌数据更新错误")
        else:
            transaction.savepoint_commit(sid)
            return Brand.objects.get(id=instance.id)

