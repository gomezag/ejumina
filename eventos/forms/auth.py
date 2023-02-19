from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UsernameField
from django.forms import TextInput, CharField, PasswordInput

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(
        widget=TextInput(attrs={'autofocus': True}),
        label="Usuario",
    )
    password = CharField(
        label= "Contraseña",
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
