from django.contrib import admin
from django.urls import path, include
from api.views import LoginAPI, Eventos

urlpatterns = [
    path('user/login', LoginAPI.as_view()),
    path('evento/upcoming', Eventos.as_view()),
    path('evento/all', Eventos.as_view())
]
