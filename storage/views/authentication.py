from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.views.generic import FormView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from ..forms import LoginForm


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('storage:storage')

    def form_valid(self, form):
        cd = form.cleaned_data
        user = authenticate(username=cd['username'], password=cd['password'])
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return super().form_valid(form)
            else:
                return HttpResponse('Account disabled')
        else:
            messages.error(self.request, 'Неправильное имя пользователя или пароль')
            return self.form_invalid(form)

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('storage:login')