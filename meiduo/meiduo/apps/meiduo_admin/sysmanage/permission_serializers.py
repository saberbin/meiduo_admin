from rest_framework import serializers
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from users.models import User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class PermissionContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ("id", "name")


class PermissionGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class PermissionGroupSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "name")


class PermissionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def create(self, validated_data):
        # save the user
        user = super().create(validated_data)

        user.is_staff = True
        user.is_superuser = True
        # set the password
        user.set_password(validated_data["password"])
        user.save()

        return user

    # 重写upload方法更新数据
    def update(self, instance, validated_data):
        super().update(instance, validated_data)

        if validated_data["password"]:
            instance.set_password(validated_data["password"])

        instance.save()
        return instance


class PermissionUserGroupSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")
