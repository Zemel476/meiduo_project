# -*- coding: utf-8 -*-
# @Time    : 2025/8/11 17:58
# @Author  : 老冰棍
# @File    : crons.py
# @Software: PyCharm
import time

from apps.contents.models import ContentCategory
from utils.goods import get_categories


def generic_meiduo_index():
    print('--------------%s-------------'%time.ctime())
    # 1.商品分类数据
    categories = get_categories()
    # 2.广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 我们的首页 后边会讲解页面静态化
    # 我们把数据 传递 给 模板
    context = {
        'categories': categories,
        'contents': contents,
    }

    # 1. 加载渲染的模板
    from django.template import loader
    index_template=loader.get_template('index.html')

    # 2. 把数据给模板
    index_html_data=index_template.render(context)
    # 3. 把渲染好的HTML，写入到指定文件
    from meiduo_mall import settings
    import os
    # base_dir 的上一级
    file_path=os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/index.html')

    with open(file_path,'w',encoding='utf-8') as f:
        f.write(index_html_data)