from rest_framework import serializers
from .models import PaymentTransaction
from crucial.models import StudentProfile, Fees, PartialPayment


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['id', 'village', 'post_office', 'ps_or_upazilla', 'district']


class MarkFeesPaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fees
        fields = ['id', 'status']  

class PaymentTransactionSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    gateway_url = serializers.SerializerMethodField() 

    def validate_tran_id(self, value):
        """Validate that transaction ID starts with 'TXN_' or 'API_'."""
        if not (value.startswith('TXN_') or value.startswith('API_')):
            raise serializers.ValidationError("Invalid transaction ID format.")
        return value

    def get_gateway_url(self, obj):
        """Return the payment gateway URL if applicable."""
        if obj.status == 'PENDING':
            ssl_config = SSLC.objects.first()
            if ssl_config:
                if ssl_config.store_penv == 'sandbox':
                    return f"https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY={obj.tran_id}"
                return f"https://securepay.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY={obj.tran_id}"
        return None

    class Meta:
        model = PaymentTransaction
        fields = [
            'tran_id', 'amount', 'status', 'tran_date',
            'val_id', 'bank_tran_id', 'currency',
            'card_type', 'card_no', 'student_profile',
            'accounting_completed', 'gateway_url'
        ]
        read_only_fields = ['val_id', 'bank_tran_id', 'card_type', 'card_no', 'accounting_completed']

from datetime import timedelta
from crucial.models import StudentProfile, Fees, PartialPayment

class FeeTypeSerializer(serializers.Serializer):
    fee_type = serializers.CharField()
    month_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

from datetime import timedelta
from accounting.models import Receive
from crucial.models import Fees, PartialPayment

class PaymentTransactionSerializerTwo(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student_profile.student_field.name', read_only=True)
    student_roll = serializers.IntegerField(source='student_profile.roll_no', read_only=True)
    fee_details = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'gateway', 'tran_id', 'amount', 'status', 'tran_date', 'val_id',
            'bank_tran_id', 'currency', 'card_type', 'card_no', 'student_name',
            'student_roll', 'accounting_completed', 'receipt_pdf', 'fee_details'
        ]
        read_only_fields = fields

    def get_fee_details(self, obj):
        # Get transaction time with buffer
        transaction_time = obj.tran_date
        time_threshold = transaction_time + timedelta(minutes=5)
        
        # Find matching Receive entries for this transaction
        receives = Receive.objects.filter(
            created_at__gte=transaction_time - timedelta(minutes=1),
            created_at__lte=time_threshold,
            student=obj.student_profile,
            description__icontains=obj.tran_id 
        ).order_by('created_at')
        
        fee_details = []
        used_fee_ids = set()
        
        for receive in receives:
            # Find Fees records updated around the same time as Receive creation
            fees = Fees.objects.filter(
                student_id=obj.student_profile,
                updated_at__gte=receive.created_at - timedelta(seconds=30),
                updated_at__lte=receive.created_at + timedelta(seconds=30),
            ).exclude(id__in=used_fee_ids)
            
            # Find partial payments linked to these fees
            for fee in fees:
                partial_payments = PartialPayment.objects.filter(
                    fee=fee,
                    payment_date__gte=receive.created_at - timedelta(seconds=30),
                    payment_date__lte=receive.created_at + timedelta(seconds=30),
                )
                
                for payment in partial_payments:
                    if fee.id not in used_fee_ids:
                        fee_details.append({
                            "fee_type": fee.feetype_id.fees_title,
                            "month_name": fee.month_id.name if fee.month_id else "N/A",
                            "amount": float(payment.amount)
                        })
                        used_fee_ids.add(fee.id)
        
        return fee_details
    
    
