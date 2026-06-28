from django.forms import ModelForm
from .models import *
from crucial.models import TeacherSubjectAssign
from django import forms
from user.models import RoleType


class Yearform(ModelForm):
    class Meta:
        model=Admission_Year
        fields=['name']

class Classform(ModelForm):
    class Meta:
        model=StudentClass 
        fields=['name']

class Groupform(ModelForm):
    class Meta:
        model=StuGroup
        fields=['name']
        
class Sectionform(ModelForm):
    class Meta:
        model=StudentSection
        fields=['name']

class Subjectform(ModelForm):
    class Meta:
        model=Subject
        fields=['name']

class Shiftform(ModelForm):
    class Meta:
        model=StudentShift
        fields=['name']

class Periodform(ModelForm):
    class Meta:
        model=Period
        fields=['name']

class MarkTypeform(ModelForm):
    class Meta:
        model=Mark_type
        fields=['name']

class ClassConfigform(ModelForm):
    class Meta:
        model=ClassConfig
        fields= '__all__'
        

class PeriodConfigform(ModelForm):
    class Meta:
        model=PeriodConfig
        fields= '__all__'

class TeacherSubjectAssignform(ModelForm):
    class Meta:
        model=TeacherSubjectAssign
        fields= '__all__'

class SubjectAssignForm(ModelForm):
    class Meta: 
        model = SubjectAssign
        fields = ['class_id', 'subjects']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple,
        }

class SubjectConfigForm(ModelForm):
    class Meta:
        model =SubjectConfig
        fields= '__all__' 



class Markconfigform(ModelForm):
    class Meta:
        model = Mark_config
        fields = '__all__'

class RoleTypeForm(ModelForm):
    class Meta:
        model = RoleType
        fields = '__all__'

    