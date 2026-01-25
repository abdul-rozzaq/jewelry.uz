from rest_framework import serializers

from apps.processes.models import ProcessType
from .process_template import ProcessTemplateSerializer


class ProcessTypeSerializer(serializers.ModelSerializer):
    template = ProcessTemplateSerializer()

    class Meta:
        model = ProcessType
        fields = "__all__"
