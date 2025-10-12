from rest_framework.viewsets import ModelViewSet

from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
