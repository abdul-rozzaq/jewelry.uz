from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, viewsets


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
