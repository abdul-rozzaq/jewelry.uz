from django.utils.timezone import now

from django.db.models import Sum, Count, ExpressionWrapper, F, FloatField
from django.db.models.functions import TruncDate, ExtractWeekDay

from django.utils.timezone import timedelta

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.dashboard.serializers import DashboardStatsSerializer
from apps.processes.models import Process, ProcessStatus
from apps.products.models import Product
from apps.organizations.models import Organization
from apps.transactions.models import Transaction

fifteen_minutes = 15 * 60


class DashboardStatisticsAPIView(ListAPIView):
    serializer_class = DashboardStatsSerializer

    # @cache_response(timeout=fifteen_minutes)
    def get(self, request, *args, **kwargs):
        today = now().date()
        user = request.user

        products = Product.objects.filter(organization=user.organization).aggregate(
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

        transactions = Transaction.objects.filter(created_at__date=today, receiver=user.organization).aggregate(
            count=Count("id"),
            total_quantity=Sum("items__quantity"),
        )

        transactions_last_week = (
            Transaction.objects.filter(receiver=user.organization, created_at__date__gte=today - timedelta(days=7))
            .annotate(day=TruncDate("created_at"), weekday=ExtractWeekDay("created_at"))  # 1=Yakshanba, 2=Dushanba, ..., 7=Shanba
            .values("day", "weekday")
            .annotate(
                count=Count("id"),
            )
            .order_by("day")
        )

        transactions_count = transactions["count"] or 0
        transactions_total = transactions["total_quantity"] or 0

        loses = (
            Process.objects.filter(status=ProcessStatus.COMPLETED, organization=user.organization)
            .annotate(
                lost_quantity=F("total_in") - F("total_out"),
            )
            .aggregate(
                total_lost_quantity=Sum("lost_quantity"),
            )
        )

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
                "last_week": list(transactions_last_week),
            },
            "gold": {
                "total": gold_quantity,
            },
            "loses": {
                "total": loses["total_lost_quantity"] or 0,
            },
        }

        return Response(response)
