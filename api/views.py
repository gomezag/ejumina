from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .permissions import UsuarioEsRRPP, UsuarioEsAdmin, UsuarioEsBouncer, UsuarioEsAdminOrRRPP
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from eventos.models import *
from .serializers import *
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class LoginAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = LoginUserSerializer

    def get(self):
        return Response()

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data={
            'username': request.data.get('CI', None),
            'password': request.data.get('password', None)
        })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token = RefreshToken.for_user(user)

        return Response({
            "_id": user.pk,
            "rol": user.groups.first().label,
            "CI": "0000000",
            "access": str(token.access_token),
            "refresh": str(token)
        }, status=status.HTTP_200_OK)


class Eventos(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Lista de Eventos
        :param request:
        :param format:
        :return:
        """
        eventos = UpcomingEventosSerializer(data=
            Evento.objects.all(), many=True)
        eventos.is_valid()
        return Response({
            'eventos': eventos.data
        })


    def post(self, request, format=None):
        """
        Crea un Evento
        :param request:
        :param format:
        :return:
        """

    def put(self, request, format=None):
        """
        Edita
        :param request:
        :param format:
        :return:
        """

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


class Personas(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UsuarioEsAdminOrRRPP]

    def get(self, request, format=None):
        """
        Lista de Personas
        :param request:
        :param format:
        :return:
        """

