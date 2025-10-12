from rest_framework.permissions import IsAuthenticated

from apps.processes.models import Process
from apps.users.models import User


class CanDeleteProcess(IsAuthenticated):

    def has_object_permission(self, request, view, obj: Process):

        user: User = request.user

        return user.organization and user.organization == obj.organization
