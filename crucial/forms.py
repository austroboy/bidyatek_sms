from django.forms import ModelForm
from .models import *
from core.models import Subject

from django import forms
 

class RoutineFormSET(forms.ModelForm):
    
    class Meta:
        model = Routine
        fields = ['class_id', 'period_id', 'day_name', 'subject_id', 'teacher_name', 'id']


class Feetypeform(ModelForm):
    class Meta:
        model=Feetype
        fields='__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].disabled = True

class Hosteltypeform(ModelForm):
    class Meta:
        model=Hostel_package
        fields='__all__'

class Tutiontypeform(ModelForm):
    class Meta:
        model=Tution_package
        fields='__all__'

class Transporttypeform(ModelForm):
    class Meta:
        model=Transport_package
        fields='__all__'

class Fee_package_form(ModelForm):
    class Meta:
        model=Fee_package
        fields='__all__'

# class Waiverform(ModelForm):
#     class Meta:
#         model=Waiver
#         fields='__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['created_by'].disabled = True

class WaiverForm(forms.ModelForm):
    fee_types = forms.ModelMultipleChoiceField(
        queryset=Feetype.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Waiver
        fields = ['student_id', 'waiver_amount', 'description', 'fee_types']

class Expensetypeform(ModelForm):
    class Meta:
        model=ExpenseHead
        fields=['expensetype']

class Expenselistform(ModelForm): 
    class Meta:
        model = Expenseitemlist
        fields = ['expensetype_id','name', 'amount', 'employee_id','expense_date', 'attach_doc', 'description', 'academic_year','created_by','updated_by']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].disabled = True

class IncomeHeadform(ModelForm):
    class Meta:
        model=IncomeHead
        fields=['incometype']

class Incomelistform(ModelForm): 
    class Meta:
        model = IncomeitemList
        fields = ['incometype_id','name','invoice_number', 'amount', 'income_date', 'attach_doc', 'description', 'academic_year','created_by','updated_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].disabled = True

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = ['amount', 'received_by', 'note', 'created_by','updated_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].disabled = True

class Addition_type_form(ModelForm):
    class Meta:
        model=Addition_type
        fields='__all__'

class Deduction_type_form(ModelForm):
    class Meta:
        model=Deduction_type
        fields='__all__'

class SalaryConfFrom(ModelForm):
    class Meta:
        model=SalaryConfiguration
        fields= ['employee','basic_salary','created_by','updated_by'] 

    def __init__(self, *args, **kwargs):
        super(SalaryConfFrom, self).__init__(*args, **kwargs)
        self.fields['created_by'].disabled = True
        self.fields['employee'].widget.attrs['readonly'] = 'readonly'

class SalaryIncrementform(forms.ModelForm):
    class Meta:
        model = SalaryIncrement
        fields = ['employee', 'is_percentage', 'increment_amount', 'effective_date']

class SalaryAdvanceform(forms.ModelForm):
    class Meta:
        model = AdvanceSalaryPayment
        fields='__all__'

class Homeworkform(ModelForm):
    class Meta:
        model=Homework
        fields= '__all__'

class Noticeform(ModelForm):
    class Meta:
        model=Notice
        fields= '__all__'

class Notificationform(ModelForm):
    class Meta:
        model=Notification
        fields= '__all__'

class SMSTemplateform(ModelForm):
    class Meta:
        model= SMSTemplate
        fields= '__all__'


class TeacherAssignForm(ModelForm):
    class Meta:
        model = TeacherSubjectAssign
        fields = ['teacher_id', 'subject_assigns', 'academic_year']
        widgets = {
            'subject_assigns': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(TeacherAssignForm, self).__init__(*args, **kwargs)
        self.fields['academic_year'].widget.attrs['readonly'] = True


#Fee Forms #########################################################


class FeeHeadForm(forms.ModelForm):
    class Meta:
        model = FeeHead
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Fee Head Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Description'}),
        }

class FeeSubHeadForm(forms.ModelForm):
    class Meta:
        model = FeeSubHead
        fields = ['head', 'name', 'description']
        widgets = {
            'head': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Sub Head Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Description'}),
        }
        

class FeeSubHeadConfigForm(forms.ModelForm):
    sub_heads = forms.ModelMultipleChoiceField(
        queryset=FeeSubHead.objects.all(),
        widget=forms.CheckboxSelectMultiple,  
        required=True,
    )

    class Meta:
        model = FeeSubHeadConfig
        fields = ['head', 'sub_heads', 'is_active']

        

class FeeSubHeadConfigForm(forms.ModelForm):
    sub_heads = forms.ModelMultipleChoiceField(
        queryset=FeeSubHead.objects.all(),
        widget=forms.CheckboxSelectMultiple,  
        required=True,
    )

    class Meta:
        model = FeeSubHeadConfig
        fields = ['head', 'sub_heads', 'is_active']
        

class SalaryProcessForm(forms.Form):
    INVOICE_CHOICES = [
        ('bulk', 'Bulk'),
        ('individual', 'Individual'),
    ]
    SALARY_MONTH_CHOICES = [
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ]

    invoice_type = forms.ChoiceField(
        choices=INVOICE_CHOICES,
        required=True,
        label="Invoice Type",
        widget=forms.Select(attrs={"class": "form-select", "id": "invoice_type"}),
    )
    salary_month = forms.ChoiceField(
        choices=SALARY_MONTH_CHOICES,
        required=True,
        label="Salary Month",
        widget=forms.Select(attrs={"class": "form-select", "id": "salary_month_id"}),
    )
    employee_id = forms.ModelChoiceField(
        queryset=SalaryConfiguration.objects.all(),
        required=False,
        label="Employee",
        widget=forms.Select(attrs={"class": "form-select", "id": "employee_id", "disabled": "true"}),
    )
    payment_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Payment Amount",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "payment_amount",
                "placeholder": "Enter Payment Amount",
                "style": "display:none;",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        invoice_type = cleaned_data.get("invoice_type")
        employee_id = cleaned_data.get("employee_id")
        payment_amount = cleaned_data.get("payment_amount")

        # Validate payment_amount for 'individual' invoice
        if invoice_type == "individual":
            if not employee_id:
                self.add_error("employee_id", "Employee is required for individual invoices.")
            if payment_amount is None or payment_amount <= 0:
                self.add_error("payment_amount", "Payment amount must be greater than zero for individual invoices.")

        return cleaned_data


class FeeReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    format = forms.ChoiceField(choices=[('pdf', 'PDF'), ('excel', 'Excel')])