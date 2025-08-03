from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# django 自带用户模型，有密码加密验证功能

class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True) # unique 唯一

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name
