from rest_framework import serializers
from goods.models import CategoryVisitCount


class UserGoodsDayCountSerializers(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CategoryVisitCount
        fields = "__all__"
