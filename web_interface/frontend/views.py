import json
import logging

from django.views.decorators.csrf import csrf_exempt

from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView
from django.http import (HttpResponseRedirect, HttpResponseBadRequest,
                         JsonResponse, HttpResponse)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Q

from .forms import LoginOrRegisterForm, NewAppForm
from . import models
from .utils import debug_only, post_only, authenticated_only

# Create your views here.


logger = logging.getLogger('django.server')


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
            logger.debug('%s entered dashboard', self.request.user)
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
    def request_logs_view(request):
        app_id = request.POST.get('app_id')
        lr = models.LogRequest.get_or_create_log_request(app_id)
        if lr.log_uploaded:
            pass
        else:
            pass

    @staticmethod
    def enable_app(request, *args, **kwargs):
        pass

    @staticmethod
    def disable_app(request, *args, **kwargs):
        pass


class Api:

    @staticmethod
    @csrf_exempt
    def login(request):
        if request.method == 'POST':
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse(status=201)
        return HttpResponseBadRequest()

    @staticmethod
    @authenticated_only
    def get_all_apps(request):
        apps = models.App.objects.all()
        return JsonResponse(
            {'response': [app.as_dict() for app in apps]},
            json_dumps_params={'indent': 4, 'separators': (',', ': ')}
        )

    @staticmethod
    def _filter_apps(*q_filters):
        apps = models.App.objects.filter(*q_filters)
        apps = [app.as_dict() for app in apps]
        return JsonResponse({'response': apps})

    @staticmethod
    @authenticated_only
    def get_apps_to_enable(request):
        return Api._filter_apps(
            Q(desired_state=models.AppStates.enabled),
            ~Q(current_state=models.AppStates.enabled)
        )

    @staticmethod
    @authenticated_only
    def get_apps_to_disable(request):
        return Api._filter_apps(
            Q(desired_state=models.AppStates.disabled),
            ~Q(current_state=models.AppStates.disabled)
        )

    @staticmethod
    @authenticated_only
    def get_apps_to_deploy(request):
        return Api._filter_apps(
            Q(desired_state=models.AppStates.deploy_needed),
            ~Q(current_state=models.AppStates.enabled)
        )

    @staticmethod
    @authenticated_only
    def get_apps_to_delete(request):
        return Api._filter_apps(
            Q(current_state=models.AppStates.delete_needed)
        )
        
    @staticmethod
    @authenticated_only
    def get_should_be_running_apps(request):
        return Api._filter_apps(
            Q(desired_state=models.AppStates.enabled)
        )

    @staticmethod
    @csrf_exempt
    @post_only
    @authenticated_only
    def set_apps_status(request):
        """ Receive JSON string like [{name: 'Name', current_state: 'enabled'}, ...]
        """
        updates = request.POST.get('updates') or request.GET.get('updates')
        if updates is None:
            return HttpResponseBadRequest()

        updates = json.loads(updates, encoding='utf-8')
        for update in updates:
            app = models.App.objects.get(name=update['name'])
            app.current_state = update['current_state']
            app.app_url = update['url']
            app.save()

        return JsonResponse({'response': 'success'})

    @staticmethod
    @authenticated_only
    def get_log_requests(request):
        pass

    @staticmethod
    @csrf_exempt
    @authenticated_only
    def post_logs(request):
        log = request.POST.get('log')
        app_id = request.POST.get('app_id')
        lr = models.LogRequest.get_or_create_log_request(app_id)
        lr.upload_file(log)
        return HttpResponse(status=200)
