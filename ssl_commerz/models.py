from django.db import models
from django.conf import settings
from user.models import StudentProfile
from crucial.models import FeeHead
import json

class SSLC(models.Model):
    store_id=models.CharField(max_length=100)
    store_pass=models.CharField(max_length=100)
    store_penv=models.CharField(max_length=30)

    def __str__(self):
        return f"{self.store_id}"


class BankDisbursementAccount(models.Model):
    BANK_CHOICES = (
        ('trust_bank', 'Trust Bank'),
        ('bank_asia', 'Bank Asia'),
        ('dutch_bangla', 'Dutch Bangla Bank'),
        ('brac_bank', 'BRAC Bank'),
        ('city_bank', 'City Bank'),
        ('eastern_bank', 'Eastern Bank'),
        ('standard_bank', 'Standard Bank'),
        ('one_bank', 'One Bank'),
        ('prime_bank', 'Prime Bank'),
        ('islami_bank', 'Islami Bank'),
        # Add more as needed
    )
    
    bank_name = models.CharField(max_length=100, choices=BANK_CHOICES)
    display_name = models.CharField(max_length=200, help_text="Display name for admin interface")
    sslcz_ref_id = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="SSLCommerz provided reference ID for this bank account"
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.display_name} ({self.sslcz_ref_id})"
    
    class Meta:
        verbose_name = "SSLCommerz Bank Account"
        verbose_name_plural = "SSLCommerz Bank Accounts"
        
class FeeHeadBankDistribution(models.Model):
    bank_account = models.ForeignKey(BankDisbursementAccount, on_delete=models.CASCADE)
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, 
                                    help_text="Percentage of this fee head to go to this bank")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['bank_account', 'fee_head']
        verbose_name = "Fee Head Bank Distribution"
        verbose_name_plural = "Fee Head Bank Distributions"
    
    def __str__(self):
        return f"{self.fee_head.name} -> {self.bank_account.get_bank_name_display()} ({self.percentage}%)"


class DisbursementConfiguration(models.Model):
    CONFIG_CHOICES = (
        ('manual', 'Manual Distribution'),
        ('percentage', 'Percentage Based'),
        ('fixed', 'Fixed Amount'),
    )
    
    config_name = models.CharField(max_length=200)
    config_type = models.CharField(max_length=20, choices=CONFIG_CHOICES, default='manual')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.config_name
    
    def get_distribution_data(self, total_amount, fee_heads):
        """Calculate distribution based on configuration type"""
        distribution = []
        
        if self.config_type == 'percentage':
            # Get fee head distributions from FeeHeadBankDistribution
            for fee_head in fee_heads:
                distributions = FeeHeadBankDistribution.objects.filter(
                    fee_head=fee_head,
                    is_active=True
                )
                for dist in distributions:
                    amount = (total_amount * dist.percentage) / 100
                    distribution.append({
                        'bank_account': dist.bank_account,
                        'amount': amount,
                        'fee_head': fee_head
                    })
        elif self.config_type == 'fixed':
            # Implement fixed amount logic if needed
            pass
        # Manual distribution will be handled in views
        
        return distribution


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )
    GATEWAY_CHOICES = (
        ('sslcommerz', 'SSLCommerz'),
        ('trustbank', 'Trust Bank'),
    )
    
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES, default='sslcommerz')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    tran_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    tran_date = models.DateTimeField(auto_now_add=True)
    val_id = models.CharField(max_length=255, blank=True, null=True)
    bank_tran_id = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, default='BDT')
    card_type = models.CharField(max_length=50, blank=True, null=True)
    card_no = models.CharField(max_length=50, blank=True, null=True)
    student_profile = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    accounting_completed = models.BooleanField(default=False)
    receipt_pdf = models.FileField(upload_to='receipts/', null=True, blank=True)
    
    # Disbursement fields
    disbursement_config = models.ForeignKey(DisbursementConfiguration, on_delete=models.SET_NULL, 
                                          null=True, blank=True)
    disbursement_data = models.JSONField(null=True, blank=True, 
                                       help_text="JSON data for bank disbursement distribution")
    is_disbursement_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.tran_id} - {self.status}"
    
    def generate_disbursement_json(self):
        if not self.disbursement_data:
            return None
        
        disbursement_list = []
        for item in self.disbursement_data:
            # Ensure amount is properly formatted as string with 2 decimal places
            try:
                amount = Decimal(item.get('raw_amount', item.get('amount', '0')))
                formatted_amount = f"{amount:.2f}"
                
                disbursement_list.append({
                    "sslcz_ref_id": item['sslcz_ref_id'],
                    "amount": formatted_amount
                })
            except (KeyError, ValueError, Decimal.InvalidOperation) as e:
                logger.error(f"Error formatting disbursement amount: {e}")
                continue
        
        return json.dumps(disbursement_list)
    
    def get_disbursement_summary(self):
        """Get human-readable disbursement summary"""
        if not self.disbursement_data:
            return "No disbursement configured"
        
        summary = []
        for item in self.disbursement_data:
            try:
                bank_account = BankDisbursementAccount.objects.get(sslcz_ref_id=item['sslcz_ref_id'])
                summary.append(f"{bank_account.get_bank_name_display()}: {item['amount']} BDT")
            except BankDisbursementAccount.DoesNotExist:
                summary.append(f"Bank ID {item['sslcz_ref_id']}: {item['amount']} BDT")
        
        return "; ".join(summary)


class TransactionDisbursement(models.Model):
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, 
                                   related_name='disbursements')
    bank_account = models.ForeignKey(BankDisbursementAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING', 
                             choices=(('PENDING', 'Pending'), ('COMPLETED', 'Completed'), 
                                     ('FAILED', 'Failed')))
    disbursement_date = models.DateTimeField(null=True, blank=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction.tran_id} - {self.bank_account} - {self.amount}"


class TrustBank(models.Model):
    merchant_key = models.CharField(max_length=100)
    merchant_password = models.CharField(max_length=100)
    merchant_name = models.CharField(max_length=100)
    base_url = models.URLField()
    is_active = models.BooleanField(default=False)  

    def __str__(self):
        return self.merchant_name