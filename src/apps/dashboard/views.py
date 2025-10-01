from django.utils.timezone import now

from django.db.models import Sum

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.dashboard.serializers import DashboardStatsSerializer
from apps.products.models import Product
from apps.organizations.models import Organization
from apps.transactions.models import Transaction


class DashboardStatisticsAPIView(ListAPIView):
    serializer_class = DashboardStatsSerializer

    def get(self, request, *args, **kwargs):
        today = now().date()
        # yesterday = today - timedelta(days=1)

        products = Product.objects.all()
        products_count = products.count()
        products_total = products.aggregate(total=Sum("quantity"))["total"] or 0

        organizations = Organization.objects.all()
        organizations_count = organizations.count()

        transactions = Transaction.objects.filter(created_at__date=today)

        transactions_count = transactions.count()
        transactions_total = transactions.aggregate(total_quantity=Sum("items__quantity"))["total_quantity"] or 0

        response = {
            "products": {
                "count": products_count,
                "total": products_total,
            },
            "organization": {
                "count": organizations_count,
            },
            "transaction": {
                "count": transactions_count,
                "total": transactions_total,
            },
        }

        return Response(response)
