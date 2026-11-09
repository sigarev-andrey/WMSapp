from django.http import HttpResponseRedirect
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info.startswith('/mobile/'):
            if not request.user.is_authenticated and request.path_info != reverse('mobile:login'):
                return redirect_to_login(request.get_full_path(), reverse('mobile:login'))
            return None
        if not request.user.is_authenticated and request.path != '/login/':
            return HttpResponseRedirect('/login/') # or http response
        return None
