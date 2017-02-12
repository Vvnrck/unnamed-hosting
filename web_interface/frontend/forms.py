from django import forms


class LoginOrRegisterForm(forms.Form):
    name = forms.CharField(label='Name', max_length=64, required=True, widget=forms.TextInput)
    password = forms.CharField(label='Password', max_length=512, required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', max_length=512, required=False, widget=forms.PasswordInput)
    is_registration = forms.BooleanField(label='I\'m new here!', required=False, widget=forms.HiddenInput)


APP_TYPE = ('static', 'static'), ('django', 'django')


class NewAppForm(forms.Form):
    app_name = forms.CharField(label='App Name', max_length=128, required=True, widget=forms.TextInput)
    repo_url = forms.CharField(label='Git repository URL', max_length=4096, required=True, widget=forms.TextInput)
    app_type = forms.ChoiceField(label='App Type', required=True, widget=forms.RadioSelect, choices=APP_TYPE)
