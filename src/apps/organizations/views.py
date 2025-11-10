from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationSerializer
from apps.transactions.models import Transaction
from apps.transactions.serializers import GetTransactionSerializer


class OrganizationViewSet(ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    @action(methods=["GET"], detail=True, serializer_class=GetTransactionSerializer)
    def transactions(self, request, *args, **kwargs):
        obj: Organization = self.get_object()

        queryset = (
            Transaction.objects.select_related("sender", "receiver", "project")
            .prefetch_related(
                "items",
                "items__product__material",
                "items__product__organization",
                "items__product__project",
            )
            .filter(Q(sender=obj) | Q(receiver=obj))
            .order_by("-id")
        )

        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        elif start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        elif end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
