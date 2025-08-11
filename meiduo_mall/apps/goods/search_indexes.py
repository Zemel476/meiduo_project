# -*- coding: utf-8 -*-
# @Time    : 2025/8/11 15:21
# @Author  : 老冰棍
# @File    : search_indexes.py
# @Software: PyCharm
from apps.goods.models import SKU
from haystack import indexes

class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    # 每个SearchIndex 字段都需要有一个字段设置（有且只有一个） document=True
    # 这是向 Haystack和搜索引擎指示哪个字段是其中搜索的主要字段
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return SKU

    def index_queryset(self, using=None):
        # SKU.objects.all()
        return self.get_model().objects.all()
