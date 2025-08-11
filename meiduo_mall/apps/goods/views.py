from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from haystack.views import SearchView

from apps.contents.models import ContentCategory
from apps.goods.models import GoodsCategory, SKU
from utils.goods import get_categories, get_breadcrumb, get_goods_specs
from utils.views import LoginRequiredJsonMixin


# Create your views here.
class IndexView(LoginRequiredJsonMixin, View):
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


class ListView(LoginRequiredJsonMixin, View):

    def get(self, request, category_id):
        ordering = request.GET.get('ordering')
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')

        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'msg': ''})

        # 获得面包屑数据
        breadcrumb = get_breadcrumb(category)

        # 查询分类对应sku数据，再排序
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering).values('id', 'name', 'price','default_image')
        # 分页
        paginator = Paginator(skus, page_size)

        page_skus = paginator.get_page(page)
        result = []
        for  sku in page_skus.object_list:
            result.append(sku)

        return JsonResponse({'code': 0, 'msg': '', 'result': result})


class SKUSearchView(LoginRequiredJsonMixin, SearchView):

    def create_response(self):
        # 获取搜索的结果
        context = self.get_context()

        sku_list = []
        for item in context['page'].object_list:
            sku_list.append({
                'id': item.object.id,
                'name': item.object.name,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count,
            })

        return JsonResponse(sku_list, safe=False)


class DetailView(LoginRequiredJsonMixin, View):

    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'msg': ''})
        # 分类数据
        categories = get_categories()
        # 面包屑
        breadcrumb = get_breadcrumb(sku.category)
        # 规格信息
        goods_specs = get_goods_specs(sku)

        context = {
            'sku': sku,
            'goods_specs': goods_specs,
            'categories': categories,
            'breadcrumb': breadcrumb,
        }

        return render(request, 'detail.html', context)