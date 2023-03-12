from django.contrib import admin
from django.urls import path, include
from api.views import *

urlpatterns = [
    path('user/login', Login.as_view()),
    path('user/login', Logout.as_view()),
    path('evento/ongoing', Eventos.as_view({'get': 'ongoing'})),
    path('evento/all', Eventos.as_view({'get': 'all'})),
    path('invitado/all', Personas.as_view({'get': 'all'})),
    path('invitado/new', Personas.as_view({'post': 'create'})),
    path('invitado/ci/<str:ci>', Personas.as_view({'get': 'find'}))
]
