from django.db.models import Q

from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework import permissions, serializers
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from apps.transactions.permissions import CanAcceptTransaction
from apps.transactions.services import TransactionService
from apps.users.models import User, UserRoles

from .models import Transaction
from .serializers import CreateTransactionSerializer, GetTransactionSerializer


class TransactionListView(ListAPIView):
    queryset = Transaction.objects.none()
    serializer_class = GetTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user: User = self.request.user

        if user.role == UserRoles.ADMIN:
            return Transaction.objects.all()

        return Transaction.objects.filter(Q(sender=user.organization) | Q(receiver=user.organization))


class TransactionCreateView(CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = CreateTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user: User = self.request.user
        serializer.save(sender=user.organization)


class TransactionDetailView(RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = GetTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


class TransactionAcceptView(GenericAPIView):
    queryset = Transaction.objects.none()
    serializer_class = GetTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, CanAcceptTransaction]

    def get_queryset(self):
        user: User = self.request.user

        if not user.is_authenticated:
            return self.queryset

        elif user.role == UserRoles.ADMIN:
            return Transaction.objects.all()

        return Transaction.objects.filter(Q(sender=user.organization) | Q(receiver=user.organization))

    @swagger_auto_schema(request_body=serializers.Serializer)
    def post(self, request, *args, **kwargs):
        transaction: Transaction = self.get_object()
        updated_tx = TransactionService.accept_transaction(transaction)

        serializer = GetTransactionSerializer(instance=updated_tx)

        return Response({"detail": f"{updated_tx} muvaffaqiyatli tasdiqlandi", "transaction": serializer.data})
