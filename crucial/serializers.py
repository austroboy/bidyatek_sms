from rest_framework import serializers
from .models import *

class FeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fees
        fields = '__all__' 

class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = '__all__' 

class FeeSerializer(serializers.ModelSerializer):
    total_due = serializers.SerializerMethodField()

    class Meta:
        model = Fees
        fields = ['id', 'student_id', 'amount', 'discount_amount', 'late_amount', 'status', 'total_due']

    def get_total_due(self, obj):
        return obj.total_fee_after_partial_payments()


class PaymentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=22, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Fees.PAYMENT_METHOD_CHOICES)      
