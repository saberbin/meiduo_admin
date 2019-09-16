from rest_framework import serializers
from goods.models import GoodsChannel, GoodsChannelGroup


class ChannelsSerializer(serializers.ModelSerializer):

    # 重写组名
    group = serializers.StringRelatedField(read_only=True)
    group_id = serializers.IntegerField()

    # 重写分类
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()

    class Meta:
        model = GoodsChannel
        fields = "__all__"


class ChannelsTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsChannelGroup
        fields = ("id", "name")
