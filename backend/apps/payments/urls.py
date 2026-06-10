from django.urls import path
from .views import AdminTransactionListView, AdminTransactionStatsView, InitiatePaymentView

urlpatterns = [
    path('v1/admin/transactions/stats', AdminTransactionStatsView.as_view(), name='admin-transactions-stats'),
    path('v1/admin/transactions', AdminTransactionListView.as_view(), name='admin-transactions'),
    path('initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
]
