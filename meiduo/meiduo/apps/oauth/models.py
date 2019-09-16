from django.db import models
# from users.models import User
from meiduo.utils.my_model import BaseModel


# 1,美多qq用户模型类
class OAuthQQUser(BaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, verbose_name="美多用户")
    open_id = models.CharField(max_length=64, unique=True, verbose_name="qq用户id")

    class Meta:
        db_table = "tb_qq_users"


# 2, 美多微博用户模型类
class OAuthSinaUser(BaseModel):
    """
    Sina登录用户数据
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    uid = models.CharField(max_length=64, verbose_name='access_token', db_index=True)

    class Meta:
        db_table = 'tb_oauth_sina'
        verbose_name = 'sina登录用户数据'
        verbose_name_plural = verbose_name

