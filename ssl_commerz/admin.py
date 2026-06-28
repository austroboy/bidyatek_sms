from django.contrib import admin
from .models import *

@admin.register(SSLC)
class SSLCAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'store_pass', 'store_penv')
    search_fields = ('store_id', 'store_penv')

@admin.register(BankDisbursementAccount)
class BankDisbursementAccountAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'bank_name', 'sslcz_ref_id', 'is_active')
    list_filter = ('bank_name', 'is_active')
    search_fields = ('display_name', 'sslcz_ref_id')
    
    fieldsets = (
        ('Bank Information', {
            'fields': ('bank_name', 'display_name', 'sslcz_ref_id', 'is_active')
        }),
    )

@admin.register(FeeHeadBankDistribution)
class FeeHeadBankDistributionAdmin(admin.ModelAdmin):
    list_display = ('fee_head', 'bank_account', 'percentage', 'is_active')
    list_filter = ('is_active', 'bank_account__bank_name')
    search_fields = ('fee_head__name', 'bank_account__account_name')

@admin.register(DisbursementConfiguration)
class DisbursementConfigurationAdmin(admin.ModelAdmin):
    list_display = ('config_name', 'config_type', 'is_active', 'created_at')
    list_filter = ('config_type', 'is_active')
    search_fields = ('config_name', 'description')

@admin.register(TransactionDisbursement)
class TransactionDisbursementAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'bank_account', 'amount', 'status', 'disbursement_date')
    list_filter = ('status', 'bank_account__bank_name', 'disbursement_date')
    search_fields = ('transaction__tran_id', 'bank_account__account_name')
    readonly_fields = ('created_at', 'updated_at')

# Update existing PaymentTransaction admin
@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('tran_id', 'user', 'amount', 'status', 'gateway', 'is_disbursement_enabled', 'tran_date')
    list_filter = ('status', 'gateway', 'is_disbursement_enabled', 'tran_date')
    search_fields = ('tran_id', 'user__username', 'student_profile__student_field__name')
    readonly_fields = ('tran_date', 'val_id', 'bank_tran_id')
    
    def disbursement_summary(self, obj):
        return obj.get_disbursement_summary()
    disbursement_summary.short_description = 'Disbursement Summary'