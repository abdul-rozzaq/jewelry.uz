from rest_framework.viewsets import ModelViewSet

from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer


class MaterialViewSet(ModelViewSet):
    serializer_class = MaterialSerializer
    queryset = Material.objects.all()
