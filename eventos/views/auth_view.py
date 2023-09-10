"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""

from django.views import View
from django.contrib.auth.forms import authenticate, AuthenticationForm
from django.shortcuts import render
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.conf import settings

from eventos.models.users import Usuario

import urllib
import os
import json


class LoginView(View):
    template_name = 'register/login.html'
    form_class = AuthenticationForm

    def get_context(self):
        c = dict()
        c['recaptcha_site_key'] = os.getenv('GOOGLE_RECAPTCHA_SITE_KEY')
        c['form'] = self.form_class()
        return c

    def get(self, request, *args, **kwargs):
        c = self.get_context()
        return render(request, self.template_name, c)

    def post(self, request, *args, **kwargs):
        captcha_error = False
        c = self.get_context()
        if settings.DEBUG:
            result = dict(success=True)
        else:
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': os.getenv("GOOGLE_RECAPTCHA_SECRET_KEY"),
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''
        if result['success']:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(
                request=request,
                username=username,
                password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    try:
                        return HttpResponseRedirect(request.GET['next'])
                    except:
                        return HttpResponseRedirect('/')
                else:
                    c['alert_msg'] = ['Usuario desactivado. Contacta con tu administrador.']
            else:
                form = self.form_class(request=request)
                print()
                c['form_error'] = form.get_invalid_login_error()
                print(form.errors)
        else:
            captcha_error = True
        c['recaptcha_error'] = captcha_error
        return render(request, self.template_name, c)

