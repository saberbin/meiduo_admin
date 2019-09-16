from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView
from .user_serializer import UserSerializer
from rest_framework.response import Response
from users.models import User
from meiduo_admin.my_paginate import MyPageNumberPagination


class UserView(ListAPIView, CreateAPIView):
    pagination_class = MyPageNumberPagination
    serializer_class = UserSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get("keyword")
        if keyword:
            return User.objects.filter(username__contains=keyword)
        else:
            return User.objects.order_by("id").all()

    # def get(self, request):
    #     users = self.get_queryset()
    #     serializer = self.get_serializer(instance=users, many=True)
    #     return Response({
    #         "lists": serializer.data,
    #         "page": 1,
    #         "pages": 5,
    #     })
    #     return self.list(request)




