from rest_framework.generics import ListAPIView

from .models import Transaction


from .serializers import TransactionSerializer


class TransactionListView(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
