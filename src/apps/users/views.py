from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import User

from .permissions import IsAdminOrSelf
from .serializers import GetUserSerializer, MyTokenObtainPairSerializer, CreateUpdateUserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUpdateUserSerializer

    def get_permissions(self):
        if self.action in ["list", "destroy", "create"]:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsAdminOrSelf]

        return [perm() for perm in permission_classes]

    def get_serializer_class(self, *args, **kwargs):

        if self.action in ["list", "retrieve"]:
            return GetUserSerializer

        return super().get_serializer_class(*args, **kwargs)

    @action(["GET"], detail=False, url_path="me")
    def get_me(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(instance=user)

        return Response(serializer.data)
