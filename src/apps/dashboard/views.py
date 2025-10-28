from django.utils.timezone import now

from django.db.models import Sum, Count, ExpressionWrapper, F, FloatField

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.dashboard.serializers import DashboardStatsSerializer
from apps.products.models import Product
from apps.organizations.models import Organization
from apps.transactions.models import Transaction

fifteen_minutes = 15 * 60


class DashboardStatisticsAPIView(ListAPIView):
    serializer_class = DashboardStatsSerializer

    # @cache_response(timeout=fifteen_minutes)
    def get(self, request, *args, **kwargs):
        today = now().date()

        products = Product.objects.aggregate(
            products_count=Count("id"),
            total_quantity=Sum("quantity"),
            gold_quantity=Sum(
                ExpressionWrapper(
                    F("quantity") * (F("purity") / 100.0),
                    output_field=FloatField(),
                )
            ),
        )

        products_count = products["products_count"] or 0
        products_total = products["total_quantity"] or 0
        gold_quantity = products["gold_quantity"] or 0

        organizations = Organization.objects.aggregate(count=Count("id"))
        organizations_count = organizations["count"] or 0

        transactions = Transaction.objects.filter(created_at__date=today).aggregate(
            count=Count("id"),
            total_quantity=Sum("items__quantity"),
        )

        transactions_count = transactions["count"] or 0
        transactions_total = transactions["total_quantity"] or 0

        response = {
            "products": {
                "count": products_count,
                "total": products_total,
            },
            "organizations": {
                "count": organizations_count,
            },
            "transactions": {
                "count": transactions_count,
                "total": transactions_total,
            },
            "gold": {
                "total": gold_quantity,
            },
        }

        return Response(response)
