from rest_framework.viewsets import ModelViewSet
from eventos.models import *
from .serializers import *
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class Login(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
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


class Logout(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Eventos(ModelViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)
    serializer_class = EventoSerializer

    def all(self, request):
        queryset = Evento.objects.all()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def ongoing(self, request):
        queryset = Evento.objects.all()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

