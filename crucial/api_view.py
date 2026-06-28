from core.models import ClassConfig
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Fees, Homework, StudentProfile
from .serializers import *

class StudentUnpaidFeesView(APIView):
    def get(self, request, student_id):
        student = get_object_or_404(StudentProfile, id=student_id)

        unpaid_fees = Fees.objects.filter(student_id=student, status='unpaid')

        serializer = FeesSerializer(unpaid_fees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class HomeworkByClassView(APIView):
    def get(self, request, class_id):
        class_instance = get_object_or_404(ClassConfig, id=class_id)

        homework_list = Homework.objects.filter(class_id=class_instance)

        if not homework_list.exists():
            return Response({"message": "No homework found for this class."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HomeworkSerializer(homework_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class StudentFeesView(APIView):
    """
    API to retrieve a student's outstanding fees.
    """
    def get(self, request, student_id):
        try:
            student = StudentProfile.objects.get(id=student_id)
            fees = Fees.objects.filter(student_id=student, is_enable=True)
            serializer = FeeSerializer(fees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


class PaymentView(APIView):
    """
    API to process student fee payments.
    """
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            student_id = serializer.validated_data['student_id']
            amount_paid = serializer.validated_data['amount']
            payment_method = serializer.validated_data['payment_method']
            created_by = request.user

            try:
                student = StudentProfile.objects.get(id=student_id)
                fees = Fees.objects.filter(student_id=student, status__in=['unpaid', 'partial'])

                total_due = sum(fee.total_fee_after_partial_payments() for fee in fees)

                if amount_paid > total_due:
                    extra_amount = amount_paid - total_due
                    amount_paid = total_due  # Deduct only the required amount

                for fee in fees:
                    if amount_paid <= 0:
                        break
                    remaining_fee = fee.total_fee_after_partial_payments()
                    payment_amount = min(amount_paid, remaining_fee)

                    fee.record_payment(payment_amount, created_by)
                    amount_paid -= payment_amount

                return Response({"message": "Payment recorded successfully"}, status=status.HTTP_200_OK)

            except StudentProfile.DoesNotExist:
                return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

