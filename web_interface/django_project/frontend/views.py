from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from .forms import LoginOrRegisterForm, NewAppForm
from . import models

# Create your views here.


class LoginOrRegisterView(FormView):
    template_name = 'login.html'
    form_class = LoginOrRegisterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'login_form': LoginOrRegisterForm()
        })
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return HttpResponseRedirect(reverse('login'))
        name = form.cleaned_data['name']
        password = form.cleaned_data['password']
        is_reg = form.cleaned_data['is_registration']
        auth_method = User.objects.create_user if is_reg else authenticate
        user = auth_method(username=name, password=password)
        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect(reverse('dashboard'))


class Dashboard:

    class DashboardView(TemplateView):
        template_name = 'dashboard.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context.update({
                'apps': models.App.objects.filter(owner=self.request.user),
                'app_types': models.AppType,
                'new_app_form': NewAppForm()
            })
            return context

    class NewAppView(FormView):
        form_class = NewAppForm

        def post(self, request, *args, **kwargs):
            form = self.get_form()
            if form.is_valid():
                models.App.new_app(
                    request.user,
                    form.cleaned_data['app_name'],
                    form.cleaned_data['repo_url'],
                    form.cleaned_data['app_type']
                )
            return HttpResponseRedirect(reverse('dashboard'))

    @staticmethod
    def enable_app(request, *args, **kwargs):
        pass

    @staticmethod
    def disable_app(request, *args, **kwargs):
        pass
