from django.http import JsonResponse
from django.views import View

from apps.areas.models import Area


# Create your views here.
class AreaView(View):

    def get(self, request):
        areas = Area.objects.filter(parent=None).values('id', 'name')

        result = [area for area in areas]

        return JsonResponse({'code':200, 'msg': '', 'province_list':result})

class SubAreaView(View):

    def get(self, request, id):
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

        return JsonResponse({'code':200, 'msg': '', 'sub_data':{'subs':result}})
