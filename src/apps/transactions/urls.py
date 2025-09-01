from django.urls import path

from .views import TransactionCreateView, TransactionListView, TransactionDetailView


urlpatterns = [
    path("create/", TransactionCreateView.as_view()),
    path("list/", TransactionListView.as_view()),
    path("detail/<int:pk>/", TransactionDetailView.as_view()),
]
