from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions


from .serializers import MyTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)
