# Standard Library Imports
import json
import time
from io import BytesIO
from decimal import Decimal
from datetime import datetime, timedelta
import logging

# Django Core Imports
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

# Third-Party Libraries
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from xhtml2pdf import pisa
from num2words import num2words

# Django Models
from .models import PaymentTransaction, SSLC
from crucial.models import Fees, FeeHead
from accounting.models import Ledger, LedgerCategory, Receive

# Serializers and External APIs
from .serializers import PaymentTransactionSerializer, PaymentTransactionSerializerTwo
from sslcommerz_lib import SSLCOMMERZ

# Transactions
from django.db import transaction as db_transaction

logger = logging.getLogger(__name__)

class InitiatePaymentAPI(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        student_profile = user.student_profile.first()

        if not student_profile:
            return Response({"error": "No student profile found"}, status=status.HTTP_400_BAD_REQUEST)

        unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
        total_amount = sum(fee.total_fee_after_partial_payments() for fee in unpaid_fees)

        if total_amount <= Decimal('0.00'):
            return Response({"error": "No unpaid fees"}, status=status.HTTP_400_BAD_REQUEST)

        tran_id = f"API_{user.id}_{int(time.time())}"
        transaction = PaymentTransaction.objects.create(
            user=user,
            student_profile=student_profile,
            tran_id=tran_id,
            amount=total_amount,
            status='PENDING'
        )

        ssl_config = SSLC.objects.first()
        if not ssl_config:
            return Response({"error": "Payment gateway configuration not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        sslcz = SSLCOMMERZ({
            'store_id': ssl_config.store_id,
            'store_pass': ssl_config.store_pass,
            'issandbox': (ssl_config.store_penv == 'sandbox')
        })

        post_body = self._build_payload(request, transaction)
        try:
            response = sslcz.createSession(post_body)
            if response.get('status') == 'SUCCESS':
                gateway_url = self.get_gateway_url(response, ssl_config.store_penv)
                return Response({
                    'tran_id': tran_id,
                    'amount': total_amount,
                    'gateway_url': gateway_url,
                    'status': 'INITIATED'
                }, status=status.HTTP_201_CREATED)

            error_msg = response.get('failedreason', 'Payment initiation failed')
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"SSLCommerz API Error: {str(e)}", exc_info=True)
            transaction.status = 'FAILED'
            transaction.save()
            return Response({"error": "Payment gateway connection failed"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def _build_payload(self, request, transaction):
        student_profile = transaction.student_profile
        return {
            'total_amount': str(transaction.amount),
            'currency': "BDT",
            'tran_id': transaction.tran_id,
            'success_url': 'https://' + request.get_host() + reverse('ssl_commerz:ssl_success'),
            'fail_url': 'https://' + request.get_host() + reverse('ssl_commerz:ssl_fail'),
            'cancel_url': 'https://' + request.get_host() + reverse('ssl_commerz:ssl_cancel'),
            'ipn_url': 'https://' + request.get_host() + reverse('ssl_commerz:ipn_listener'),
            'emi_option': "0",
            'cus_name': request.user.name, 
            'cus_email': request.user.email or "example@email.com",
            'cus_phone': self.get_parent_phone(student_profile),
            'cus_add1': self.get_parent_address(student_profile)[:250],
            'cus_city': "Dhaka",
            'cus_country': "Bangladesh",
            'shipping_method': "NO",
            'product_name': "Student Fee",
            'product_category': "Fees",
            'product_profile': "general",
        }

    def get_parent_phone(self, student_profile):
        if student_profile.parent_id and student_profile.parent_id.phone_number:
            return student_profile.parent_id.phone_number
        return student_profile.student_field.phone_number or "N/A"

    def get_parent_address(self, student_profile):
        address_parts = [
            student_profile.village,
            student_profile.post_office,
            student_profile.ps_or_upazilla,
            student_profile.district
        ]
        return ", ".join(filter(None, address_parts))

    def get_gateway_url(self, response, store_penv):
        if store_penv == 'sandbox':
            return f"https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY={response['sessionkey']}"
        return response['GatewayPageURL']


class PaymentStatusAPI(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, tran_id):
        transaction = get_object_or_404(PaymentTransaction, tran_id=tran_id, user=request.user)

        if transaction.status == 'PENDING':
            ssl_config = SSLC.objects.first()
            if not ssl_config:
                return Response({"error": "Payment gateway configuration not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            sslcz = SSLCOMMERZ({
                'store_id': ssl_config.store_id,
                'store_pass': ssl_config.store_pass,
                'issandbox': (ssl_config.store_penv == 'sandbox')
            })

            try:
                tran_response = sslcz.transaction_query_tranid(tran_id)
                logger.info(f"Transaction query response for {tran_id}: {tran_response}")

                elements = tran_response.get('element', [])
                if elements:
                    element = elements[0]
                    if element.get('status') == 'VALID':
                        with db_transaction.atomic():
                            self._process_successful_transaction(transaction, element)
                    else:
                        transaction.status = 'FAILED'
                        transaction.save()
                        return Response({"error": f"Transaction failed: {element.get('status')}"}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                logger.error(f"Error checking transaction status for {tran_id}: {str(e)}", exc_info=True)
                return Response({"error": "Error processing payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = PaymentTransactionSerializer(transaction)
        return Response(serializer.data)

    def _process_successful_transaction(self, transaction, element):
        transaction.status = 'SUCCESS'
        transaction.val_id = element.get('val_id')
        transaction.bank_tran_id = element.get('bank_tran_id')
        transaction.card_type = element.get('card_type')
        transaction.card_no = element.get('card_no')
        transaction.save()

        unpaid_fees = Fees.objects.filter(student_id=transaction.student_profile).exclude(status='paid')
        for fee in unpaid_fees:
            remaining_amount = fee.total_fee() - fee.total_paid_amount()
            if remaining_amount > 0:
                PartialPayment.objects.create(fee=fee, amount=remaining_amount, created_by=transaction.user)
                fee.update_fee_status()
                fee.save()

        self._update_accounting(transaction)

    def _update_accounting(self, transaction):
        income_category, _ = LedgerCategory.objects.get_or_create(name='Income', defaults={'description': 'Income category'})
        tuition_ledger, _ = Ledger.objects.get_or_create(name='Tuition Fees Income', defaults={'category': income_category, 'code': 'TFI001', 'balance_type': 'Credit'})
        cash_ledger = Ledger.objects.get(name='Cash', category__name='Asset')

        Receive.objects.create(
            voucher_no=f"RECV-{transaction.tran_id}",
            date=timezone.now().date(),
            amount=transaction.amount,
            student=transaction.student_profile,
            fee_head=FeeHead.objects.get_or_create(name='Tuition Fees')[0],
            cash_ledger=cash_ledger,
            income_ledger=tuition_ledger,
            description=f"Payment via SSLCommerz ({transaction.tran_id})"
        )



from rest_framework.decorators import api_view, permission_classes
from .views import payment_receipt  

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_payment_receipt(request, tran_id):
#     """API endpoint for PDF receipt generation"""
#     try:
#         response = payment_receipt(request, tran_id)
#         response['Content-Type'] = 'application/pdf'
#         return response
#     except Exception as e:
#         return Response(
#             {'error': str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
        
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import PaymentTransaction
from django.http import Http404
import calendar
from .views import payment_receipt  

class TransactionMonthAPI(APIView):
    """
    API to get list of months with transactions
    Example response:
    [
        {
            "year": 2024,
            "month": 3,
            "month_name": "March",
            "transaction_count": 5
        }
    ]
    """
    def get(self, request):
        months = PaymentTransaction.objects.filter(
            user=request.user,
            status='SUCCESS'
        ).annotate(
            month=TruncMonth('tran_date')
        ).values('month').annotate(
            transaction_count=Count('id')
        ).order_by('-month')
        
        data = []
        for entry in months:
            month_date = entry['month']
            data.append({
                "year": month_date.year,
                "month": month_date.month,
                "month_name": calendar.month_name[month_date.month],
                "transaction_count": entry['transaction_count']
            })
        
        return Response(data)

from django.urls import reverse

class TransactionListAPI(APIView):
    def get(self, request, year, month):
        transactions = PaymentTransaction.objects.filter(
            user=request.user,
            status='SUCCESS',
            tran_date__year=year,
            tran_date__month=month
        ).order_by('-tran_date')
        
        data = []
        for transaction in transactions:
            data.append({
                "tran_id": transaction.tran_id,
                "amount": str(transaction.amount),
                "date": transaction.tran_date.strftime("%Y-%m-%d %H:%M:%S"),
                "receipt_url": reverse(
                    'ssl_commerz:api_receipt_download',
                    kwargs={'tran_id': transaction.tran_id}
                )
            })
        return Response(data)
        
class ReceiptDownloadAPI(APIView):
    """
    API to download PDF receipt
    """
    def get(self, request, tran_id):
        try:
            transaction = PaymentTransaction.objects.get(
                tran_id=tran_id,
                user=request.user
            )
            
            # Reuse existing payment_receipt view logic
            response = payment_receipt(request, tran_id)
            return response
            
        except PaymentTransaction.DoesNotExist:
            raise Http404("Transaction not found")

from .serializers import PaymentTransactionSerializer, PaymentTransactionSerializerTwo
from rest_framework import generics, permissions
class StudentPaymentTransactionListAPIView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializerTwo
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        return PaymentTransaction.objects.filter(
            status='SUCCESS',
            student_profile__student_field=user
        ).select_related(
            'student_profile',
            'student_profile__student_field'
        ).prefetch_related(
            'student_profile__fees_set__partial_payments'
        ).order_by('-tran_date')
        
        
        
        
class PaymentReceiptAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, tran_id):
        try:
            transaction = get_object_or_404(PaymentTransaction, tran_id=tran_id, student_profile__student_field=request.user)
            
            if transaction.tran_date.year == 2025 and transaction.tran_date.month == 2:
                return Response(
                    {"detail": "PDF downloads are temporarily unavailable for February 2025"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if transaction.receipt_pdf:
                response = HttpResponse(transaction.receipt_pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="receipt_{tran_id}.pdf"'
                return response
                
            student_profile = transaction.student_profile
            
            time_threshold = transaction.tran_date + timedelta(minutes=1)
            partial_payments = PartialPayment.objects.filter(
                fee__student_id=student_profile,
                payment_date__gte=transaction.tran_date,
                payment_date__lte=time_threshold,
                created_by=transaction.user
            ).select_related('fee__feetype_id')
            
            fee_heads = {}
            total_paid = Decimal('0.00')
            
            if transaction.gateway == 'trustbank' and not partial_payments.exists():
                fee_heads["Trust Bank Payment"] = transaction.amount
                total_paid = transaction.amount
            else:
                for payment in partial_payments:
                    fee_type = payment.fee.feetype_id.fees_title if payment.fee.feetype_id else "Miscellaneous"
                    fee_heads[fee_type] = fee_heads.get(fee_type, Decimal('0.00')) + payment.amount
                    total_paid += payment.amount

            context = {
                'name': student_profile.student_field.name,
                'student_id': student_profile.roll_no or "N/A", 
                'shift': student_profile.class_id.shift_id.name if student_profile.class_id.shift_id else "N/A",
                'version': student_profile.get_version_display(),
                'payment_time': transaction.tran_date.strftime("%Y-%m-%d %H:%M:%S"),
                'transaction_id': tran_id,
                'class': student_profile.class_id.class_group_id.class_id.name,
                'section': student_profile.class_id.section_id.name if student_profile.class_id.section_id else "N/A",
                'group': student_profile.class_id.class_group_id.group_id.name if student_profile.class_id.class_group_id.group_id else "N/A",
                'payment_type': transaction.card_type or transaction.get_gateway_display(),
                'fee_heads': [{'name': k, 'amount': v} for k, v in fee_heads.items()],
                'total': total_paid,
                'total_in_words': num2words(total_paid, lang='en').title() + " Taka Only",
            }

            template = get_template('ssl_commerz/payment_receipt.html')
            html = template.render(context)
            
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
            
            if pisa_status.err:
                logger.error("PDF creation failed")
                return Response(
                    {"detail": "Error generating PDF"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            try:
                pdf_buffer.seek(0)
                transaction.receipt_pdf.save(
                    f'receipts/{tran_id}.pdf',
                    ContentFile(pdf_buffer.read()),
                    save=False
                )
                transaction.save()
            except Exception as e:
                logger.warning(f"PDF save failed: {str(e)} (proceeding with download)")

            pdf_buffer.seek(0)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt_{tran_id}.pdf"'
            return response

        except Exception as e:
            logger.error(f"Receipt generation failed: {str(e)}")
            return Response(
                {"detail": "Error generating receipt"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionMonthListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        months = PaymentTransaction.objects.filter(
            student_profile__student_field=request.user, 
            status='SUCCESS'
        ).annotate(
            month=TruncMonth('tran_date')
        ).values('month').annotate(
            total=Count('id')
        ).order_by('-month')
        
        return Response({
            'months': list(months)
        })


class TransactionMonthDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year, month):
        start_date = make_aware(datetime(year, month, 1))
        end_date = start_date + timedelta(days=31)
        
        transactions = PaymentTransaction.objects.filter(
            student_profile__student_field=request.user,
            status='SUCCESS',
            tran_date__gte=start_date,
            tran_date__lt=end_date
        ).order_by('-tran_date')
        
        is_feb_2025 = (year == 2025 and month == 2)
        
        return Response({
            'transactions': [
                {
                    'tran_id': t.tran_id,
                    'amount': str(t.amount),
                    'tran_date': t.tran_date,
                    'gateway': t.gateway,
                    'card_type': t.card_type,
                    'receipt_available': bool(t.receipt_pdf)
                } for t in transactions
            ],
            'month': f"{year}-{month:02d}",
            'is_feb_2025': is_feb_2025
        })