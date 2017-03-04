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
        app_id = request.GET.get('app_id')
        app = models.App.objects.get(pk=app_id)
        if app.owner != request.user:
            # TODO: add message
            return HttpResponseRedirect(reverse('dashboard'))
        with app.log_file_path.open(mode='rb') as logs:
            response = HttpResponse(content=logs)
            response['Content-Type'] = 'text/plain'
            response['Content-Disposition'] = 'attachment; filename="logs.txt"'
            return response


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
            
            print(app.desired_state == models.AppStates.deploy_needed)
            if app.desired_state == str(models.AppStates.deploy_needed):
                app.desired_state = models.AppStates.enabled
            print(app.desired_state, models.AppStates.deploy_needed)
            app.save()

        return JsonResponse({'response': 'success'})

    @staticmethod
    @csrf_exempt
    @authenticated_only
    def accept_logs(request):
        app_name = request.POST['app_name']
        try:
            app = models.App.objects.get(name=app_name)
            with app.log_file_path.open(mode='w') as logs:
                logs.write(request.POST['logs'])
        except models.App.DoesNotExist:
            pass
        return JsonResponse({'response': 'success'})

