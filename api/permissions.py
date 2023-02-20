from rest_framework.permissions import BasePermission
from ..eventos.models import Usuario
from django.db.models import ObjectDoesNotExist


class UsuarioEsRRPP(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            try:
                usuario = Usuario.objects.get(user=request.user)
                return [usuario.rol] == [i for i, v in Usuario.ROLES_USUARIO if v == 'R.R.P.P.']
            except ObjectDoesNotExist:
                return False
        else:
            return False


class UsuarioEsBouncer(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            try:
                usuario = Usuario.objects.get(user=request.user)
                return [usuario.rol] == [i for i, v in Usuario.ROLES_USUARIO if v == 'Bouncer']
            except ObjectDoesNotExist:
                return False
        else:
            return False


class UsuarioEsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            try:
                usuario = Usuario.objects.get(user=request.user)
                return [usuario.rol] == [i for i, v in Usuario.ROLES_USUARIO if v == 'Admin']
            except ObjectDoesNotExist:
                return False
        else:
            return False


class UsuarioEsAdminOrRRPP(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            try:
                usuario = Usuario.objects.get(user=request.user)
                return usuario.rol in [i for i, v in Usuario.ROLES_USUARIO if v in ['Admin', 'R.R.P.P.']]
            except ObjectDoesNotExist:
                return False
        else:
            return False


