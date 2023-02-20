from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .permissions import UsuarioEsRRPP, UsuarioEsAdmin, UsuarioEsBouncer, UsuarioEsAdminOrRRPP
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from eventos.models import *


class EventoRRPPView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [UsuarioEsRRPP]

    def get(self, request, format=None):
        """
        Vista basica de Evento para un RRPP
        :param request:
        :param format:
        :return:
            - ['invitados'] Una lista de invitados a un evento, con su lista correspondiente.
            -
        """


class EventoBouncerView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [UsuarioEsBouncer]

    def get(self, request, format=None):
        """
        Vista basica de los invitados de un RRPP
        :param request:
        :param format:
        :return:
        """
        bouncer_raw = request.get('user', None)
        evento_raw = request.get('evento', None)
        try:
            evento = Evento.objects.filter(name=evento_raw)
        except ObjectDoesNotExist:
            return Response(status=500, data='No se encuentra el evento!')
        # Permission class deberia asegurar que esto exista.
        user = Usuario.objects.get(nombre=bouncer_raw)
        # TODO: Eventos deberia tener usuarios (rrpp o bouncer) habilitados para verlo.
        invitacion_set = Invitacion.objects.filter(evento=evento)
        personas = Persona.objects.filter(invitacion_set)


class RRPPView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [UsuarioEsRRPP]

    def get(self, request, format=None):
        """
        Vista basica de los invitados de un RRPP
        :param request:
        :param format:
        :return:
        """


class Eventos(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Lista de Eventos
        :param request:
        :param format:
        :return:
        """

    @permission_classes([UsuarioEsAdmin])
    def post(self, request, format=None):
        """
        Crea un Evento
        :param request:
        :param format:
        :return:
        """

    @permission_classes([UsuarioEsAdmin])
    def put(self, request, format=None):
        """
        Edita
        :param request:
        :param format:
        :return:
        """


class Personas(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Lista de Personas
        :param request:
        :param format:
        :return:
        """

    @permission_classes([UsuarioEsAdminOrRRPP])
    def post(self, request, format=None):
        """
        Crea un Evento
        :param request:
        :param format:
        :return:
        """

    @permission_classes([UsuarioEsAdmin])
    def put(self, request, format=None):
        """
        Edita
        :param request:
        :param format:
        :return:
        """
