from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import exceptions

from apps.processes.models import Process, ProcessStatus, ProcessType
from apps.processes.permissions import CanDeleteProcess
from apps.processes.serializers import CreateProcessSerializer, GetProcessSerializer, ProcessTypeSerializer, UpdateProcessSerializer
from apps.processes.service import ProcessService
from apps.users.models import User, UserRoles


class BaseQuerysetMixin:
    queryset = Process.objects.none()

    def get_queryset(self):
        user: User = self.request.user

        qs = Process.objects.all().order_by("-id")

        if not user.is_authenticated:
            return self.queryset

        if user.role == UserRoles.ADMIN:
            return qs

        return qs.filter(organization=user.organization)


class ProcessListApiView(BaseQuerysetMixin, ListAPIView):
    serializer_class = GetProcessSerializer


class ProcessRetrieveApiView(BaseQuerysetMixin, RetrieveAPIView):
    serializer_class = GetProcessSerializer


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

        if user.is_authenticated:
            return Process.objects.filter(organization=user.organization)

        return self.queryset

    def post(self, request, *args, **kwargs):
        object: Process = self.get_object()

        if object.status != ProcessStatus.IN_PROCESS:
            raise exceptions.ValidationError({"detail": "Process allaqachon tasdiqlangan"})

        process = ProcessService.complete_process(object)

        serializer = self.get_serializer(process)

        return Response(serializer.data)


class ProcessUpdateApiView(BaseQuerysetMixin, UpdateAPIView):
    serializer_class = UpdateProcessSerializer


class ProcessDestroyApiView(DestroyAPIView):
    queryset = Process.objects.all()
    permission_classes = [CanDeleteProcess]


class ProcessTypeListView(ListAPIView):
    queryset = ProcessType.objects.all()
    serializer_class = ProcessTypeSerializer
