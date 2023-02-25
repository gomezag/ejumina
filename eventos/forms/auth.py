from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import Group
import django.forms as forms
from eventos.models import Usuario


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True}),
        label="Usuario",
    )
    password = forms.CharField(
        label= "Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )


class NewUserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'groups', 'first_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].queryset = Group.objects.exclude(name='superuser')
        self.fields['password'].widget = forms.PasswordInput()