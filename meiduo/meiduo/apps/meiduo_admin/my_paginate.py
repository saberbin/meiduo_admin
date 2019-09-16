from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class MyPageNumberPagination(PageNumberPagination):
    # 默认页面大小
    page_size = 1
    # 指定页面大小的查询参数
    page_size_query_param = "pagesize"
    # 指定每页大小
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pages', self.page.paginator.num_pages),
            ('page', self.page.number),
            ('lists', data)]
            ))
