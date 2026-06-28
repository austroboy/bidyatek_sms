from django.urls import path
from . import views
from .api_views import *
app_name = 'ssl_commerz'

urlpatterns = [
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('ipn/', views.ipn_listener, name='ipn_listener'),
    path('success/', views.payment_success, name='ssl_success'),
    path('fail/', views.payment_fail, name='ssl_fail'),
    path('cancel/', views.payment_cancel, name='ssl_cancel'),
    path('ipn-listener/', views.ipn_listener, name='ipn_listener'),
    
    path('receipt/<str:tran_id>/', views.payment_receipt, name='payment_receipt'),
    path('transaction-months/', views.transaction_month_list, name='transaction_months'),
    path('transactions/<int:year>/<int:month>/', views.transaction_month_detail, name='transaction_month_detail'),
    
    # Disbursement URLs
    path('admin/disbursement-setup/<str:tran_id>/', views.admin_disbursement_setup, name='admin_disbursement_setup'),
    path('admin/review-disbursement/<str:tran_id>/', views.review_disbursement, name='review_disbursement'),
    path('admin/process-disbursement/<str:tran_id>/', views.process_disbursement_payment, name='process_disbursement_payment'),
    path('api/get-fee-heads/', views.get_fee_heads_for_student, name='get_fee_heads'),
    
    # API
    path('api/initiate-payment/', InitiatePaymentAPI.as_view(), name='api_initiate_payment'),
    path('api/payment-status/<str:tran_id>/', PaymentStatusAPI.as_view(), name='api_payment_status'),
    path('api/transaction-months/', TransactionMonthAPI.as_view(), name='api-transaction-months'),
    path('api/transactions/<int:year>/<int:month>/', TransactionListAPI.as_view(), name='api-transaction-list'),
    path('api/receipts/<str:tran_id>/', ReceiptDownloadAPI.as_view(), name='api_receipt_download'),
    path('api/student/payments/successful/',StudentPaymentTransactionListAPIView.as_view(),name='student-payments-list'), 
    
    path('api/payments/receipt/<str:tran_id>/', PaymentReceiptAPIView.as_view(), name='api-payment-receipt'),
    path('api/payments/months/', TransactionMonthListAPIView.as_view(), name='api-transaction-months'),
    path('api/payments/months/<int:year>/<int:month>/', TransactionMonthDetailAPIView.as_view(), name='api-transaction-month-detail'),   
    
    # Trust Bank URLs (optional - kept for future use)
    path('trust/success/', views.trust_payment_success, name='trust_success'),
    path('trust/fail/', views.trust_payment_fail, name='trust_fail'),
    path('trust/cancel/', views.trust_payment_cancel, name='trust_cancel'),
]