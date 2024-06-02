from django.shortcuts import render
from django.contrib.auth.views import LoginView

def csrf_fail(request, reason=""):
    c = dict(reason=reason)
    return render(request, 'errors/csrf_fail.html', c, status=403)
