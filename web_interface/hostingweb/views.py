from django.http import HttpResponse
from django.views.generic import TemplateView


class LoginOrRegisterView(TemplateView):
    template_name = "home.html"

    def post(self, request):
        pass
