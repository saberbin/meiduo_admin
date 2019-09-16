from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="create_time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="update_time")

    class Meta:
        abstract = True
