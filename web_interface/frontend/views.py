import hashlib
import json

from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView
from django.http import (HttpResponseRedirect, HttpResponseBadRequest,
                         JsonResponse, HttpResponse)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.db.models import Q

from .forms import LoginOrRegisterForm, NewAppForm
from . import models

# Create your views here.


class LoginOrRegisterView(FormView):
    template_name = 'login.html'
    form_class = LoginOrRegisterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'view_name': 'login',
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
                'view_name': 'dashboard',
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
                    owner=request.user,
                    app_name=form.cleaned_data['app_name'],
                    repo_url=form.cleaned_data['repo_url'],
                    app_type=form.cleaned_data['app_type']
                )
            return HttpResponseRedirect(reverse('dashboard'))

    class DeleteAppView(FormView):
        def post(self, request, *args, **kwargs):
            models.App.objects.get(pk=request.POST['id']).delete()
            return HttpResponse(status=201)

    @staticmethod
    def enable_app(request, *args, **kwargs):
        pass

    @staticmethod
    def disable_app(request, *args, **kwargs):
        pass


class Api:

    @staticmethod
    def get_all_apps(request):
        if not settings.DEBUG:
            return HttpResponseBadRequest()

        apps = models.App.objects.all()
        apps = [{
            'id': app.id,
            'repo_url': app.repo_url,
            'app_status': app.current_state,
            'desired_status': app.desired_state,
            'app_type': app.app_type,
            'app_path': app.app_path,
            'app_url': app.app_url
        } for app in apps]
        return JsonResponse(
            {'response': apps},
            json_dumps_params={'indent': 4, 'separators': (',', ': ')}
        )

    @staticmethod
    def get_apps_to_enable(request):
        if not settings.DEBUG and request.method != 'POST':
            return HttpResponseBadRequest()

        key_digest = hashlib.sha512(request.POST.get('key', b''))
        if not settings.DEBUG and key_digest != settings.HOSTING_DAEMON_SECRET:
            return HttpResponseBadRequest()

        apps = models.App.objects.filter(
            Q(desired_state=models.AppStates.enabled),
            ~Q(current_state=models.AppStates.enabled)
        )
        apps = [{
            'id': app.id,
            'repo_url': app.repo_url,
            'app_type': app.app_type,
            'app_path': app.app_path,
            'app_url': app.app_url
        } for app in apps]
        return JsonResponse({'response': apps})

    @staticmethod
    def get_apps_to_disable(request):
        if not settings.DEBUG and request.method != 'POST':
            return HttpResponseBadRequest()

        key_digest = hashlib.sha512(request.POST.get('key', b''))
        if not settings.DEBUG and key_digest != settings.HOSTING_DAEMON_SECRET:
            return HttpResponseBadRequest()

        apps = models.App.objects.filter(
            Q(desired_state=models.AppStates.disabled),
            ~Q(current_state=models.AppStates.disabled)
        )
        apps = [{
            'id': app.id,
            'repo_url': app.repo_url,
            'app_type': app.app_type,
            'app_path': app.app_path,
            'app_url': app.app_url
        } for app in apps]
        return JsonResponse(apps)

    @staticmethod
    def set_apps_status(request):
        if not settings.DEBUG and request.method != 'POST':
            return HttpResponseBadRequest()

        key_digest = hashlib.sha512(request.POST.get('key', b''))
        if not settings.DEBUG and key_digest != settings.HOSTING_DAEMON_SECRET:
            return HttpResponseBadRequest()

        updates = request.POST.get('updates') or request.GET.get('updates')
        if updates is None:
            return HttpResponseBadRequest()

        updates = json.loads(updates, encoding='utf-8')
        for update in updates:
            app = models.App.objects.get(id=update['id'])
            app.current_state = update['current_state']
            app.save()

        return HttpResponse(status=201)