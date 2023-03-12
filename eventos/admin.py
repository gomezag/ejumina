"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.admin import UserAdmin
from eventos.models import Usuario

# Register your models here.

app_models = apps.get_app_config('eventos').get_models()
for model in app_models:
    try:
        if model != Usuario:
            admin.site.register(model)
        else:
            admin.site.register(model, UserAdmin)
    except AlreadyRegistered:
        pass