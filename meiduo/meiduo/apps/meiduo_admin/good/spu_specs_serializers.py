from rest_framework import serializers
from goods.models import SPUSpecification, SpecificationOption


# spces序列化器
class SPUSpecsSerializer(serializers.ModelSerializer):
    # 重写spu
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = "__all__"


# specs option serializer
class SPecsOptionSerializer(serializers.ModelSerializer):
    # 重写spec
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = "__all__"


# ｓｐｅｃ规格信息
class SpecsSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPUSpecification
        fields = ("id", "name")
