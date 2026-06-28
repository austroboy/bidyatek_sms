from django import forms
from .models import *

class LedgerCategoryForm(forms.ModelForm):
    class Meta:
        model = LedgerCategory
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.Select(choices=LedgerCategory.CATEGORY_TYPES),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class LedgerForm(forms.ModelForm):
    class Meta:
        model = Ledger
        fields = ['category', 'name', 'code', 'opening_balance', 'balance_type', 'is_active', 'description']
        widgets = {
            'balance_type': forms.Select(choices=Ledger.BALANCE_TYPES),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class LedgerEntryForm(forms.ModelForm):
    class Meta:
        model = LedgerEntry
        fields = ['ledger', 'entry_type', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class ReceiveForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cash_ledger'].queryset = Ledger.objects.filter(category__name='Asset')
        self.fields['income_ledger'].queryset = Ledger.objects.filter(category__name='Income')

    class Meta:
        model = Receive
        fields = ['voucher_no', 'date', 'amount', 'student', 'fee_head', 
                 'cash_ledger', 'income_ledger', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense_ledger'].queryset = Ledger.objects.filter(category__name='Expense')
        self.fields['cash_ledger'].queryset = Ledger.objects.filter(category__name='Asset')

    class Meta:
        model = Payment
        fields = ['voucher_no', 'date', 'amount', 'staff', 
                 'expense_ledger', 'cash_ledger', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ContraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_ledger'].queryset = Ledger.objects.filter(category__name='Asset')
        self.fields['to_ledger'].queryset = Ledger.objects.filter(category__name='Asset')

    class Meta:
        model = Contra
        fields = ['voucher_no', 'date', 'amount', 'from_ledger', 'to_ledger', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['voucher_no', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['ledger', 'entry_type', 'amount', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

# Formset for Journal Entries
JournalEntryFormSet = forms.inlineformset_factory(
    Journal,
    JournalEntry,
    form=JournalEntryForm,
    extra=2,
    can_delete=True
)