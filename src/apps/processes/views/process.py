from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import exceptions

from apps.processes.models import Process, ProcessStatus
from apps.processes.serializers import CreateProcessSerializer, GetProcessSerializer
from apps.processes.services import ProcessService
from apps.users.models import User, UserRoles


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

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class ProcessCompleteApiView(CreateAPIView):
    queryset = Process.objects.none()
    serializer_class = GetProcessSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return self.queryset

        return Process.objects.filter(organization=user.organization)

    def post(self, request, *args, **kwargs):
        object: Process = self.get_object()

        if object.status != ProcessStatus.IN_PROCESS:
            raise exceptions.ValidationError({"detail": "Process allaqachon tasdiqlangan"})

        process = ProcessService.complete_process(object)

        serializer = self.get_serializer(process)

        return Response(serializer.data)
