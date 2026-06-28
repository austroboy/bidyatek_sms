from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from user.models import StaffProfile, StudentProfile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F

class LedgerCategory(models.Model):
    CATEGORY_TYPES = [
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Equity', 'Equity'),
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_TYPES, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Ledger Categories"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Ledger(models.Model):
    BALANCE_TYPES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]
    
    category = models.ForeignKey(LedgerCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_type = models.CharField(max_length=6, choices=BALANCE_TYPES)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def current_balance(self):
        debit_total = self.entries.filter(entry_type='Debit').aggregate(
            total=models.Sum('amount'))['total'] or 0
        credit_total = self.entries.filter(entry_type='Credit').aggregate(
            total=models.Sum('amount'))['total'] or 0
        
        if self.balance_type == 'Debit':
            return self.opening_balance + debit_total - credit_total
        return self.opening_balance + credit_total - debit_total

class EntryHead(models.Model):
    name= models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

class LedgerEntry(models.Model):
    ENTRY_TYPES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]
    
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='entries')
    entry_type = models.CharField(max_length=6, choices=ENTRY_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    sub_ledg= models.ForeignKey(EntryHead, null= True, blank= True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Ledger Entries"
        ordering = ['-date']

    def __str__(self):
        return f"{self.ledger.name} - {self.entry_type} {self.amount}"



# ====================
# TRANSACTION MODELS
# ====================

class Receive(models.Model):
    voucher_no = models.CharField(max_length=50, unique=True)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    fee_head = models.ForeignKey('crucial.FeeHead', on_delete=models.SET_NULL, null=True, blank=True)
    cash_ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, related_name='receives')
    income_ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, related_name='income_receipts')
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(StaffProfile, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"RECV-{self.voucher_no}"

    def clean(self):
        if self.cash_ledger.category.name != 'Asset':
            raise ValidationError("Cash ledger must be an Asset account")
        if self.income_ledger.category.name != 'Income':
            raise ValidationError("Income ledger must be an Income account")

@receiver(post_save, sender=Receive)
def process_receive_transaction(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            if not instance.cash_ledger or not instance.income_ledger:
                raise ValueError("Missing ledger information, transaction cannot be recorded.")

            LedgerEntry.objects.create(
                ledger=instance.cash_ledger,
                entry_type='Debit',
                amount=instance.amount,
                date=instance.date,
                description=f"Cash receipt from {instance.student or 'general'}"
            )

            LedgerEntry.objects.create(
                ledger=instance.income_ledger,
                entry_type='Credit',
                amount=instance.amount,
                date=instance.date,
                description=f"Income recorded for {instance.fee_head or 'general'}"
            )

            # main_balance, created = MainBalance.objects.get_or_create(cash_ledger=instance.cash_ledger)
            # main_balance.balance = F('balance') + instance.amount
            # main_balance.save(update_fields=['balance'])

            journal = Journal.objects.create(
                voucher_no=f"JRNL-RECV-{instance.voucher_no}",
                date=instance.date,
                description=instance.description,
                created_by=instance.created_by
            )

            JournalEntry.objects.create(
                journal=journal,
                ledger=instance.cash_ledger,
                entry_type='Debit',
                amount=instance.amount,
                description=f"Cash receipt from {instance.student or 'general'}"
            )

            JournalEntry.objects.create(
                journal=journal,
                ledger=instance.income_ledger,
                entry_type='Credit',
                amount=instance.amount,
                description=f"Income recorded for {instance.fee_head or 'general'}"
            )


class Payment(models.Model):    
    voucher_no = models.CharField(max_length=50, unique=True)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, 
                            null=True, blank=True, related_name='staff_payments')
    expense_ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, 
                                     related_name='expense_payments')
    cash_ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT,
                                  related_name='cash_payments')
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(StaffProfile, on_delete=models.PROTECT, related_name='created_payments',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"PAY-{self.voucher_no}"

@receiver(post_save, sender=Payment)
def process_payment_transaction(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            if not instance.cash_ledger or not instance.expense_ledger:
                raise ValueError("Missing ledger information, transaction cannot be recorded.")

            LedgerEntry.objects.create(
                ledger=instance.cash_ledger,
                entry_type='Credit',
                amount=instance.amount,
                date=instance.date,
                description="Cash disbursement for payment"
            )

            LedgerEntry.objects.create(
                ledger=instance.expense_ledger,
                entry_type='Debit',
                amount=instance.amount,
                date=instance.date,
                description=f"Expense payment to {instance.staff or 'vendor'}"
            )

            # cash_main_balance, created = MainBalance.objects.get_or_create(cash_ledger=instance.cash_ledger)
            # cash_main_balance.balance = instance.cash_ledger.current_balance
            # cash_main_balance.save(update_fields=['balance'])

            journal = Journal.objects.create(
                voucher_no=f"JRNL-PAY-{instance.voucher_no}",
                date=instance.date,
                description=instance.description,
                created_by=instance.created_by
            )

            JournalEntry.objects.create(
                journal=journal,
                ledger=instance.expense_ledger,
                entry_type='Debit',
                amount=instance.amount,
                description=f"Expense payment to {instance.staff or 'vendor'}"
            )

            JournalEntry.objects.create(
                journal=journal,
                ledger=instance.cash_ledger,
                entry_type='Credit',
                amount=instance.amount,
                description="Cash disbursement for payment"
            )
         
class Contra(models.Model):
    voucher_no = models.CharField(max_length=50, unique=True)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    from_ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, related_name='contra_out')
    to_ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, related_name='contra_in')
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(StaffProfile, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"CONTRA-{self.voucher_no}"

    def clean(self):
        if self.from_ledger.category.name != 'Asset' or self.to_ledger.category.name != 'Asset':
            raise ValidationError("Both ledgers must be Asset accounts")
        
        
@receiver(post_save, sender=Contra)
def process_contra_transaction(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            # From Ledger (Asset) - Credit
            LedgerEntry.objects.create(
                ledger=instance.from_ledger,
                entry_type='Credit',
                amount=instance.amount,
                date=instance.date,
                description=f"Contra to {instance.to_ledger.name} - {instance.description}"
            )
            
            # To Ledger (Asset) - Debit
            LedgerEntry.objects.create(
                ledger=instance.to_ledger,
                entry_type='Debit',
                amount=instance.amount,
                date=instance.date,
                description=f"Contra from {instance.from_ledger.name} - {instance.description}"
            )


class Journal(models.Model):
    voucher_no = models.CharField(max_length=50, unique=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(StaffProfile, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"JRNL-{self.voucher_no}"

class JournalEntry(models.Model):
    ENTRY_TYPES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]
    
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='entries')
    ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT)
    entry_type = models.CharField(max_length=6, choices=ENTRY_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.journal.voucher_no} - {self.entry_type} {self.amount}"


class MainBalance(models.Model):
    cash_ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, limit_choices_to={'category__name': 'Asset'})
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    as_of_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cash Balance: {self.balance} as of {self.as_of_date}"

    @classmethod
    def update_balance(cls):
        cash_ledger = Ledger.objects.get(name='Cash in Hand')  
        balance = cash_ledger.current_balance
        main_balance, created = cls.objects.get_or_create()
        main_balance.cash_ledger = cash_ledger
        main_balance.balance = balance
        main_balance.save()

@receiver(post_save, sender=LedgerEntry)
@receiver(post_delete, sender=LedgerEntry)
def update_main_balance(sender, instance, **kwargs):
    try:
        cash_ledger = Ledger.objects.filter(name='Cash in Hand').first()
        
        if not cash_ledger:
            print("Error: Cash in Hand ledger not found. Balance update skipped.")
            return  

        balance = cash_ledger.current_balance
        main_balance, created = MainBalance.objects.get_or_create(cash_ledger=cash_ledger)

        if main_balance.balance != balance:
            main_balance.balance = balance
            main_balance.save(update_fields=['balance'])

    except ObjectDoesNotExist:
        print("Error: Ledger not found. Skipping main balance update.")
    except Exception as e:
        print(f"Unexpected error: {e}")   

       
# Balance Statement
class BalanceStatement(models.Model):
    balance_change = models.DecimalField(max_digits=22, decimal_places=2, default=0.00)
    statement = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.statement


# Income Head
class IncomeHead(models.Model):
    incometype = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.incometype


# Expense Head
class ExpenseHead(models.Model):
    expensetype = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.expensetype


# Income Item List
class IncomeItemList(models.Model):
    incometype_id = models.ForeignKey(IncomeHead, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    income_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=0.00)
    attach_doc = models.ImageField(upload_to="income", blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.incometype_id} - {self.name}"


# Expense Item List
class ExpenseItemList(models.Model):
    expensetype_id = models.ForeignKey(ExpenseHead, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    transaction_no = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=0.00)
    expense_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.expensetype_id} - {self.name}"


# Withdraw
class Withdraw(models.Model):
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=0.00)
    received_by = models.CharField(max_length=100, blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.received_by)
