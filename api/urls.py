from django.contrib import admin
from django.urls import path, include
from api.views import LoginAPI

urlpatterns = [
    path('user/login', LoginAPI.as_view())
]
