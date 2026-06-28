from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import SalaryProcess
from accounting.models import *
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=SalaryProcess)
def create_salary_payment_and_journal(sender, instance, created, **kwargs):
    print(f"Signal triggered for SalaryProcess {instance.id}")

    if instance.salary_status != 'paid' or not instance.payment_method:
        print(f"Skipping payment creation. Invalid salary_status: {instance.salary_status}, payment_method: {instance.payment_method}")
        return

    try:
        # Salaries Payable Ledger
        salaries_payable_ledger, _ = Ledger.objects.get_or_create(
            name="Salaries Payable",
            defaults={"category": LedgerCategory.objects.get_or_create(name="Liabilities")[0]}
        )

        # Credit Ledger Based on Payment Method
        payment_ledger_category = {
            "cash": "Cash and Cash Equivalence",
            "bank": "Bank",
            "mfs": "Mobile Financial Services"
        }
        credit_ledger = Ledger.objects.filter(
            category__name=payment_ledger_category.get(instance.payment_method)
        ).first()

        if not credit_ledger:
            raise ValueError(f"No ledger found for payment method: {instance.payment_method}")

        # Create Payment Entry
        Payment.objects.create(
            payment_for=salaries_payable_ledger,
            amount=Decimal(instance.total_salary),
            date=instance.payment_date.date(),
            voucher_no=instance.transaction_no,
            description=f"Salary payment for {instance.salary_month}",
            total_amount=Decimal(instance.total_salary),
        )

        # Create Journal Transactions
        JournalTransaction.objects.create(
            ledger=salaries_payable_ledger,
            debit_amount=Decimal(instance.total_salary),
            credit_amount=0,
            transaction_date=instance.payment_date.date(),
            voucher_no=instance.transaction_no,
            note=f"Debit entry for salary payment {instance.salary_month}",
        )

        JournalTransaction.objects.create(
            ledger=credit_ledger,
            debit_amount=0,
            credit_amount=Decimal(instance.total_salary),
            transaction_date=instance.payment_date.date(),
            voucher_no=instance.transaction_no,
            note=f"Credit entry for salary payment {instance.salary_month}",
        )

    except Exception as e:
        logger.error(f"Error processing salary payment for SalaryProcess {instance.id}: {e}")
        print(f"Error: {e}")
