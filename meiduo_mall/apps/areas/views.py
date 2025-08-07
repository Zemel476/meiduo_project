from django.core.cache import cache
from django.http import JsonResponse
from django.views import View

from apps.areas.models import Area


# Create your views here.
class AreaView(View):

    def get(self, request):
        # 设置缓存
        result = cache.get('province')

        if not result:
            areas = Area.objects.filter(parent=None).values('id', 'name')

            result = [area for area in areas]
            cache.set('province', result, 24 * 3600)

        return JsonResponse({'code':200, 'msg': '', 'province_list':result})

class SubAreaView(View):

    def get(self, request, id):
        # 设置缓存
        result = cache.get('city:{}'.format(id))

        if not result:
            # 方法一
            # areas = Area.objects.filter(parent=id)

            # 方法二
            try:
                up_level = Area.objects.get(id=id)
            except Area.DoesNotExist:
                result = []
            else:
                areas = up_level.subs.all().values('id', 'name')

                result = [area for area in areas]

                cache.set('city:{}'.format(id), result, 24 * 3600)

        return JsonResponse({'code':200, 'msg': '', 'sub_data':{'subs':result}})
