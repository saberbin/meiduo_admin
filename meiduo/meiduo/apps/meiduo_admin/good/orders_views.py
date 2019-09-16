from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from orders.models import OrderInfo, OrderGoods
from meiduo_admin.my_paginate import MyPageNumberPagination
from meiduo_admin.good import orders_serializers
from rest_framework.decorators import action


class OrdersViewSet(ModelViewSet):
    serializer_class = orders_serializers.OrdersSerializer
    # queryset = OrderInfo.objects.order_by("id").all()
    pagination_class = MyPageNumberPagination

    # overwrite the get query set function
    def get_queryset(self):
        keyword = self.request.query_params.get("keyword", "")
        queryset = OrderInfo.objects.filter(order_id__contains=keyword).order_by("order_id").all()
        return queryset


class OrderDetailView(RetrieveAPIView):
    serializer_class = orders_serializers.OrderDetailSerializer
    queryset = OrderInfo.objects.all()


class OrdersReaderOnlyViewSet(ReadOnlyModelViewSet):
    pagination_class = MyPageNumberPagination

    # overwrite the get serializer function
    def get_serializer_class(self):
        if self.action == "list":
            return orders_serializers.OrdersSerializer
        else:
            return orders_serializers.OrderDetailSerializer

    # overwrite the get query set function
    def get_queryset(self):
        if self.action == "list":
            keyword = self.request.query_params.get("keyword", "")
            queryset = OrderInfo.objects.filter(order_id__contains=keyword).order_by("order_id").all()
            return queryset
        else:
            return OrderInfo.objects.order_by("order_id").all()

    @action(methods=["PUT"], detail=True)
    def status(self, request, *args, **kwargs):
        stat = request.data.get("status")
        order = self.get_object()

        if not stat:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        order.status = stat
        order.save()
        return Response(status=status.HTTP_200_OK)

