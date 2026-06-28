from django import forms
from .models import Student, Parent, Staff
from .models import StaffProfile,StudentProfile,ParentProfile
from core.models import Admission_Year, ClassConfig,AcademicSession
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EditUserForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['phone_number', 'name','avatar', 'gender', 'dob', 'nid', 'email','religion','blood_group']

class StudentForm(UserCreationForm):
    password1 = None
    password2 = None
    class Meta:
        model = Student
        fields = ['phone_number', 'name', 'gender', 'dob', 'nid', 'email','religion','blood_group', 'rfid','user_id','avatar','present_address','permanent_address']
        
    admission_year_id = forms.ModelChoiceField(queryset=Admission_Year.objects.all(), required=False)
    academic_session_year = forms.ModelChoiceField(queryset=AcademicSession.objects.all(), required=False)
    class_id = forms.ModelChoiceField(queryset=ClassConfig.objects.all(), required=False)
    roll_no = forms.IntegerField(required=False)
    birth_certificate_no= forms.CharField(max_length=50, required=False)
    nationality= forms.CharField(max_length=50, required=False)
    tc_no=forms.CharField(max_length=50, required=False)
    admission_date = forms.DateField(required=False)
    parent_id = forms.ModelChoiceField(queryset=Parent.objects.all(), required=False)
    guardian_name = forms.CharField(max_length=50, required=False)
    father_name = forms.CharField(max_length=50, required=False)
    father_mobile_no = forms.CharField(max_length=15, required=False)
    mother_name = forms.CharField(max_length=50, required=False)
    mother_mobile_no = forms.CharField(max_length=15, required=False) 
    relation = forms.CharField(max_length=30, required=False)
    guardian_phone_number = forms.CharField(max_length=15, required=False)
    guardian_occupation = forms.CharField(max_length=50, required=False)
    guardian_nid = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

class StudentEditForm(forms.ModelForm):
    
    class Meta:
        model = Student
        fields = ['phone_number', 'name','avatar', 'gender', 'dob', 'nid', 'email','religion','blood_group', 'rfid','user_id','present_address','permanent_address']
         
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['admission_year_id','academic_session_year', 'class_id', 'roll_no','birth_certificate_no','nationality','tc_no','admission_date', 'parent_id'] 

    
# class TeacherRegistrationForm(UserCreationForm):
#     password1 = None
#     password2 = None
#     class Meta:
#         model = Teacher
#         fields = [
#             'username','phone_number','name','avatar','gender','religion','dob','blood_group','email','nid','rfid','present_address','permanent_address','disability_info','user_id'
#         ]

    

 
# class TeacherEditRegistrationForm(forms.ModelForm):
    
#     class Meta:
#         model = Teacher
#         fields = [
#             'phone_number','name','avatar','gender','religion','dob','blood_group','email','nid','rfid','present_address','permanent_address','disability_info','user_id'
#         ]


# class StaffProfileForm(forms.ModelForm):
#     class Meta:
#         model = StaffProfile
#         fields = [
#             'qualification', 'fathers_name', 'mothers_name', 'spouse_name', 'spouse_phone_number',
#             'children_no', 'marital_status','designation', 'joining_date','employee_type'
#         ]
    
class StaffRegistrationForm(UserCreationForm):
    password1 = None
    password2 = None
    class Meta:
        model = Staff
        fields = [
            'username','phone_number','name','avatar','gender','religion','dob','blood_group','email','nid','rfid','present_address','permanent_address','disability_info','user_id','nationality'
        ]

class StaffEditRegistrationForm(forms.ModelForm):
    password1 = None
    password2 = None
    class Meta:
        model = Staff
        fields = [
            'phone_number','name','avatar','gender','religion','dob','blood_group','email','nid','rfid','present_address','permanent_address','disability_info','user_id','nationality'
        ]
 
class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = [
            'qualification', 'fathers_name', 'mothers_name', 'spouse_name', 
            'spouse_phone_number', 'children_no', 'marital_status', 'designation', 
            'joining_date', 'employee_type', 'role', 'grade', 'job_nature', 
            'department', 'shift_id', 'name_tag', 't_version', 'tin', 'subject' 
        ]

class ParentForm(UserCreationForm):
    password1 = None
    password2 = None
    class Meta:
        model=Parent
        fields=[
            'username','phone_number','name','avatar','nid'
        ]

class ParentEditForm(forms.ModelForm):

    class Meta:
        model=Parent
        fields=[
            'avatar','phone_number','name','nid'
        ]

class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields=[ 'father_name','father_mobile_no','mother_name', 'mother_mobile_no', 'relation','f_occupation'] 





from django import forms
from core.models import ClassConfig

class BulkStudentIDUpdateForm(forms.Form):
    class_config = forms.ModelChoiceField(
        queryset=ClassConfig.objects.all(),
        label="Select Class"
    )
    excel_file = forms.FileField(
        label="Excel File",
        help_text="Upload Excel file with columns: 'old_id', 'new_id'"
    )

from .models import AdmissionForm
class AdmissionFormForm(forms.ModelForm):
    class Meta:
        model = AdmissionForm
        fields = '__all__'
        
        
        
# forms.py
from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        # exclude fields the user should NOT type
        exclude = ['amount', 'registration_date', 'registration_id']
        widgets = {
            'full_name': forms.TextInput(attrs={'required': True}),
            'mobile': forms.TextInput(attrs={'required': True}),
            'occupation': forms.TextInput(attrs={'required': True}),
            'designation': forms.TextInput(attrs={'required': True}),
            'email': forms.EmailInput(attrs={'required': True}),
            'admit_year': forms.NumberInput(attrs={'required': True}),
            'passing_year': forms.NumberInput(attrs={'required': True}),
            'nid': forms.TextInput(attrs={'required': True}),
            'present_address': forms.Textarea(attrs={'required': True}),
            'permanent_address': forms.Textarea(attrs={'required': True}),
            'blood_group': forms.Select(attrs={'required': True}),
            'gender': forms.RadioSelect(),
            'marital_status': forms.RadioSelect(),
        }
