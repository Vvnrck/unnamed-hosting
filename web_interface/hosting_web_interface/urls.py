"""hosting_web_interface URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

import frontend.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', frontend.views.LoginOrRegisterView.as_view(), name='login'),
    url(r'^dashboard$', login_required(frontend.views.Dashboard.DashboardView.as_view()), name='dashboard'),
    url(r'^new-app$', login_required(frontend.views.Dashboard.NewAppView.as_view()), name='new-app'),
    url(r'^delete-app$', login_required(frontend.views.Dashboard.DeleteAppView.as_view()), name='delete-app'),

    url(r'^api/login', frontend.views.Api.login),
    url(r'^api/apps-to-enable', frontend.views.Api.get_apps_to_enable),
    url(r'^api/apps-to-disable', frontend.views.Api.get_apps_to_disable),
    url(r'^api/set-app-status', frontend.views.Api.set_apps_status),

    url(r'^debug/all-apps', frontend.views.Api.get_all_apps)
]
