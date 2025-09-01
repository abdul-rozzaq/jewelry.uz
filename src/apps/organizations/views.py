from rest_framework.viewsets import ModelViewSet

from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationSerializer


class OrganizationViewSet(ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()