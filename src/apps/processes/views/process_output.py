from rest_framework.generics import UpdateAPIView, DestroyAPIView

from apps.processes.models import ProcessOutput, ProcessStatus
from apps.processes.serializers import ProcessOutputCreateSerializer


class ProcessOutputUpdateDeleteApiView(UpdateAPIView, DestroyAPIView):
    serializer_class = ProcessOutputCreateSerializer
    queryset = ProcessOutput.objects.none()

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return self.queryset

        return ProcessOutput.objects.filter(
            process__status=ProcessStatus.IN_PROCESS,
            process__organization=user.organization,
        )
