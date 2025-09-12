from rest_framework.generics import ListAPIView, CreateAPIView

from apps.processes.models import Process
from apps.processes.serializers import CreateProcessSerializer, GetProcessSerializer
from apps.users.models import User, UserRoles

"""
class ProcessViewSet( mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet, ):
    queryset = Process.objects.none()
    serializer_class = GetProcessSerializer
    create_serializer_class = CreateProcessSerializer

    def get_queryset(self):
        user: User = self.request.user

        if not user.is_authenticated:
            return self.queryset

        if user.role == UserRoles.ADMIN:
            return Process.objects.all()

        return Process.objects.filter(organization=user.organization)

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:
            return self.serializer_class

        elif self.action in ["create", "update"]:
            return self.create_serializer_class

        return super().get_serializer_class()

    @action(["POST"], detail=True, serializer_class=serializers.Serializer)
    def complete(self, request, *args, **kwargs):
        return Response({})
"""


class ProcessListApiView(ListAPIView):
    queryset = Process.objects.none()
    serializer_class = GetProcessSerializer

    def get_queryset(self):
        user: User = self.request.user

        if not user.is_authenticated:
            return self.queryset

        if user.role == UserRoles.ADMIN:
            return Process.objects.all()

        return Process.objects.filter(organization=user.organization)


class ProcessCreateApiView(CreateAPIView):
    queryset = Process.objects.all()
    serializer_class = CreateProcessSerializer

