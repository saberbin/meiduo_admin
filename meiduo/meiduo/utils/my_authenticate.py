from django.contrib.auth.backends import ModelBackend
import re
from users.models import User


# 1,重写认证方法,设置多账号登录
class MyModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not request:
            try:
                user = User.objects.get(username=username, is_staff=True, is_superuser=True)
            except Exception as e:
                return None
            if user.check_password(password):
                return user
            return None
        else:
            try:
                if re.match(r'^1[3-9]\d{9}$', username):
                    user = User.objects.get(mobile=username)
                else:
                    user = User.objects.get(username=username)
            except Exception as e:
                print(e)
                return None
            # 2,校验密码,返回用户
            if user.check_password(password):
                return user
            else:
                return None
