from django import forms
from .models import BudgetYear, BudgetCategory, BudgetMonthlyAllocation, BudgetRevision


class BudgetYearForm(forms.ModelForm):
    class Meta:
        model = BudgetYear
        fields = ['title', 'year_start', 'year_end', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Budget 2025-2026'
            }),
            'year_start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'year_end': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes...'
            }),
        }


class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = [
            'category_type', 'income_head', 'expense_head',
            'planned_amount', 'distribution_type', 'notes'
        ]
        widgets = {
            'category_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_category_type'}),
            'income_head': forms.Select(attrs={'class': 'form-select', 'id': 'id_income_head'}),
            'expense_head': forms.Select(attrs={'class': 'form-select', 'id': 'id_expense_head'}),
            'planned_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'distribution_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional justification...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.budget_year = kwargs.pop('budget_year', None)
        super().__init__(*args, **kwargs)
        # Make heads not required at form level — validated in model clean()
        self.fields['income_head'].required = False
        self.fields['expense_head'].required = False
        self.fields['notes'].required = False

    def clean(self):
        cleaned = super().clean()
        cat_type = cleaned.get('category_type')
        income_head = cleaned.get('income_head')
        expense_head = cleaned.get('expense_head')
        if cat_type == 'INCOME' and not income_head:
            raise forms.ValidationError("Please select an income head.")
        if cat_type == 'EXPENSE' and not expense_head:
            raise forms.ValidationError("Please select an expense head.")
        return cleaned


class BudgetMonthlyAllocationForm(forms.ModelForm):
    class Meta:
        model = BudgetMonthlyAllocation
        fields = ['planned_amount']
        widgets = {
            'planned_amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0'
            }),
        }


class BudgetRevisionForm(forms.ModelForm):
    class Meta:
        model = BudgetRevision
        fields = ['new_amount', 'reason']
        widgets = {
            'new_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'New planned amount'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for revision (required)'
            }),
        }
        labels = {
            'new_amount': 'New Planned Amount (৳)',
            'reason': 'Reason for Revision',
        }
