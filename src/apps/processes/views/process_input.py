from rest_framework.generics import UpdateAPIView, DestroyAPIView
from apps.processes.models import ProcessInput, ProcessStatus
from apps.users.models import User


class ProcessInputUpdateDeleteApiView(UpdateAPIView, DestroyAPIView):
    queryset = ProcessInput.objects.none()

    def get_queryset(self):
        user: User = self.request.user

        if not user.is_authenticated:
            return self.queryset

        return ProcessInput.objects.filter(
            process__status=ProcessStatus.IN_PROCESS,
            process__organization=user.organization,
        )
