from rest_framework import serializers

from apps.organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = "__all__"


class CurrentUserOrganization(serializers.CurrentUserDefault):

    def __call__(self, serializer_field):
        request = serializer_field.context.get("request")

        if request and hasattr(request, "user") and hasattr(request.user, "organization"):
            return request.user.organization

        return None
