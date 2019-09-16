from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
import datetime
from datetime import timedelta
from .home_serializer import UserGoodsDayCountSerializers
from rest_framework.generics import GenericAPIView
from goods.models import CategoryVisitCount


# 统计所有的用户（除管理员外）
class UserTotalCountView(APIView):
    def get(self, request):
        # 获取所有的用户数量
        count = User.objects.filter(is_staff=False).count()
        return Response({
            "count": count,
        })


# 统计当天注册用户
class UserDayIncrementCountView(APIView):
    def get(self, request):
        today = datetime.date.today()
        count = User.objects.filter(date_joined__gte=today).count()
        return Response({
            "count": count,
        })


# 统计当天活跃用户
class UserDayActiveCountView(APIView):
    def get(self, request):
        today = datetime.date.today()
        count = User.objects.filter(last_login__gte=today).count()
        return Response({
            "count": count,
        })


# 统计当天下单数量
class UserDayOrdersCountView(APIView):
    def get(self, request):
        today = datetime.date.today()
        count = User.objects.filter(orderinfo__create_time__gte=today).count()
        return Response({
            "count": count,
        })


class UserMonthIncrementCountView(APIView):
    def get(self, request):
        old_date = datetime.date.today() - timedelta(days=29)

        user_list = []
        for i in range(30):
            current_date = old_date + timedelta(days=i)

            next_date = current_date + timedelta(days=1)
            count = User.objects.filter(date_joined__gte=current_date, date_joined__lt=next_date).count()

            user_list.append({
                "date": current_date,
                "count": count,
            })
        return Response(user_list)


# 统计分类每日访问量
class UserGoodsDayCountView(GenericAPIView):
    serializer_class = UserGoodsDayCountSerializers

    def get_queryset(self):
        today = datetime.date.today()
        category_visits = CategoryVisitCount.objects.filter(date=today).all()
        return category_visits

    def get(self, request):
        category_visits = self.get_queryset()
        serializer = self.get_serializer(instance=category_visits, many=True)
        return Response(serializer.data)




