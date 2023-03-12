from django.contrib import admin
from django.urls import path, include
from api.views import *

urlpatterns = [
    path('user/login', Login.as_view()),
    path('user/login', Logout.as_view()),
    path('evento/upcoming', Eventos.as_view({'get': 'upcoming'})),
    path('evento/all', Eventos.as_view({'get': 'list'}))
]
