from django.http import JsonResponse
from django.views import View

from apps.users.models import User


# Create your views here.

class UsernameCountView(View):

    def get(self, request, username, count):
        count = User.objects.filter(username=username).count()

        return JsonResponse({'count':count, 'code':200, 'errmsg': ''})