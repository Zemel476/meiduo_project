from django.shortcuts import render
from django.views import View

from apps.contents.models import ContentCategory
from utils.goods import get_categories


# Create your views here.
class IndexView(View):
    def get(self, request):
        # 商品分类数据
        categories = get_categories()
        # 广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for content in content_categories:
            # 反向查询 一的乙方 默认 [关联模型名小写]_set 可查询多的数据， 可以用 related_name 修改名称
            contents[content.key] = content.content_set.filter(category=content).count()

        # 数据模板化
        return render(request, 'index.html', {'contents': contents, 'categories': categories})