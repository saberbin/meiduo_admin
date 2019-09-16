from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission, Group
from meiduo_admin.my_paginate import MyPageNumberPagination
from rest_framework.generics import ListAPIView
from django.contrib.contenttypes.models import ContentType
from meiduo_admin.sysmanage import permission_serializers
from users.models import User


class PermissionViewSet(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = permission_serializers.PermissionSerializer
    queryset = Permission.objects.order_by("id").all()


class PermissionContentTypeView(ListAPIView):
    serializer_class = permission_serializers.PermissionContentSerializer
    queryset = ContentType.objects.all()


# 用户组权限管理
class PermissionGroupsViewSet(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = permission_serializers.PermissionGroupsSerializer
    queryset = Group.objects.order_by("id").all()


# PermissionGroupSimpleView
class PermissionGroupSimpleView(ListAPIView):
    serializer_class = permission_serializers.PermissionGroupSimpleSerializer
    queryset = Permission.objects.all()


class PermissionAdminViewSet(ModelViewSet):
    serializer_class = permission_serializers.PermissionAdminSerializer
    pagination_class = MyPageNumberPagination
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(is_staff=True, is_superuser=True).order_by("id").all()


class PermissionUserGroupSimpleView(ListAPIView):
    serializer_class = permission_serializers.PermissionUserGroupSimpleSerializer
    queryset = Group.objects.all()

