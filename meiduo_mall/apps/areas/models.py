from django.db import models

# Create your models here.
class Area(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_DEFAULT, related_name='subs', default=0, blank=True, verbose_name='上级行政区')

    # related_name 关联模型的名字
    # 默认关联模型类名 小写_set area_set
    # 可以通过 related_name 修改默认名字

    class Meta:
        db_table = 'tb_area'
        verbose_name = '省市区'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name