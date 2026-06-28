from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import *

@admin.register(LedgerCategory)
class LedgerCategoryAdmin(ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    ordering = ('code',)
    search_fields = ('name', 'code')
    list_filter = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Ledger)
class LedgerAdmin(ModelAdmin):
    list_display = ('category', 'code', 'name', 'balance_type', 'current_balance', 'is_active')
    list_filter = ('category', 'balance_type', 'is_active')
    search_fields = ('name', 'code')
    readonly_fields = ('current_balance', 'created_at', 'updated_at')
    
    @admin.display(description='Current Balance')
    def current_balance(self, obj):
        return f"{obj.current_balance:,.2f}"

@admin.register(LedgerEntry)
class LedgerEntryAdmin(ModelAdmin):
    list_display = ('date', 'ledger', 'entry_type', 'amount', 'description')
    list_filter = ('entry_type', 'date', 'ledger')
    search_fields = ('ledger__name', 'description')
    date_hierarchy = 'date'

class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Receive)
class ReceiveAdmin(ModelAdmin):
    list_display = ('voucher_no', 'date', 'student', 'fee_head', 'amount', 'cash_ledger', 'income_ledger')  
    list_filter = ('date', 'cash_ledger', 'income_ledger')
    search_fields = ('voucher_no', 'student__user__name')
    raw_id_fields = ('student', 'fee_head')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('voucher_no', 'date', 'amount')
        }),
        ('Relations', {
            'fields': ('student', 'fee_head', 'cash_ledger', 'income_ledger')
        }),
        ('Additional', {
            'fields': ('description', 'created_by', 'created_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('voucher_no', 'date', 'staff', 'amount', 'expense_ledger', 'cash_ledger')
    list_filter = ('date', 'expense_ledger', 'cash_ledger')
    search_fields = ('voucher_no', 'staff__user__name')
    raw_id_fields = ('staff',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('voucher_no', 'date', 'amount')
        }),
        ('Relations', {
            'fields': ('staff', 'expense_ledger', 'cash_ledger')
        }),
        ('Additional', {
            'fields': ('description', 'created_by', 'created_at')
        }),
    )

@admin.register(Contra)
class ContraAdmin(ModelAdmin):
    list_display = ('voucher_no', 'date', 'amount', 'from_ledger', 'to_ledger')
    list_filter = ('date', 'from_ledger', 'to_ledger')
    search_fields = ('voucher_no',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'

class JournalEntryInline(admin.TabularInline):
    model = JournalEntry
    extra = 2
    fields = ('ledger', 'entry_type', 'amount', 'description')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ledger":
            kwargs["queryset"] = Ledger.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Journal)
class JournalAdmin(ModelAdmin):
    inlines = [JournalEntryInline]
    list_display = ('voucher_no', 'date', 'total_debit', 'total_credit')
    search_fields = ('voucher_no',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    
    def total_debit(self, obj):
        return obj.entries.filter(entry_type='Debit').aggregate(total=models.Sum('amount'))['total'] or 0
    
    def total_credit(self, obj):
        return obj.entries.filter(entry_type='Credit').aggregate(total=models.Sum('amount'))['total'] or 0
    
    total_debit.short_description = 'Total Debit'
    total_credit.short_description = 'Total Credit'

@admin.register(MainBalance)
class MainBalanceAdmin(ModelAdmin):
    list_display = ('cash_ledger', 'balance', 'as_of_date')
    readonly_fields = ('balance', 'as_of_date', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Register remaining models
admin.site.register(JournalEntry)

# Customize admin site header
admin.site.site_header = "School Accounting System Administration"


# @admin.register(MainBalance)
# class MainBalanceAdmin(admin.ModelAdmin):
#     list_display = ('balance', 'created_at', 'updated_at')
#     ordering = ('-updated_at',)

@admin.register(BalanceStatement)
class BalanceStatementAdmin(admin.ModelAdmin):
    list_display = ('balance_change', 'statement', 'created_at')
    ordering = ('-created_at',)

@admin.register(IncomeHead)
class IncomeHeadAdmin(admin.ModelAdmin):
    list_display = ('incometype', 'created_at', 'updated_at')
    ordering = ('-updated_at',)

@admin.register(ExpenseHead)
class ExpenseHeadAdmin(admin.ModelAdmin):
    list_display = ('expensetype', 'created_at', 'updated_at')
    ordering = ('-updated_at',)

@admin.register(IncomeItemList)
class IncomeItemListAdmin(admin.ModelAdmin):
    list_display = ('incometype_id', 'name', 'invoice_number', 'income_date', 'amount')
    search_fields = ('name', 'invoice_number')
    list_filter = ('income_date', 'incometype_id')
    ordering = ('-income_date',)

@admin.register(ExpenseItemList)
class ExpenseItemListAdmin(admin.ModelAdmin):
    list_display = ('expensetype_id', 'name', 'transaction_no', 'amount', 'expense_date')
    search_fields = ('name', 'transaction_no')
    list_filter = ('expense_date', 'expensetype_id')
    ordering = ('-expense_date',)

@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('amount', 'received_by', 'note', 'created_at', 'updated_at')
    search_fields = ('received_by', 'note')
    ordering = ('-updated_at',)

