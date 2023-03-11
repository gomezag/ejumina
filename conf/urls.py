"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""

from django.contrib import admin
from django.urls import path, include, reverse
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from eventos.views import LoginView
from eventos.forms import UserLoginForm

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path(
        'accounts/login/',
        LoginView.as_view(
            template_name="registration/login.html",
            form_class=UserLoginForm
            ),
        name='login'
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', include('eventos.urls')),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return []

    def location(self, item):
        return reverse(item)


class FeaturedViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['login']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,
    'featured': FeaturedViewSitemap,
}

urlpatterns += [
path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
     name='django.contrib.sitemaps.views.sitemap')
    ]
