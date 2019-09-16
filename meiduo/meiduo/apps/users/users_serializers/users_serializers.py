from rest_framework import serializers
from users.models import Address


class UserAddressSerializer(serializers.ModelSerializer):
    # title = serializers.CharField(label='地址标题', max_length=30)
    province = serializers.StringRelatedField()
    city = serializers.StringRelatedField()
    district = serializers.StringRelatedField()

    class Meta:
        model = Address
        fields = "__all__"

    # def update(self, instance, validated_data):
    #     title = validated_data.pop("title")
    #     pass


