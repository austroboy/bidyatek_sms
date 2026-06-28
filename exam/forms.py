from django.forms import ModelForm
from .models import *
from django import forms
from core.models import SubjectAssign


class Examnameform(ModelForm):
    class Meta:
        model=Examname
        fields=['name','start_date','end_date','academic_year']

class SyllabusForm(ModelForm):
    class Meta:
        model = Syllabus
        fields = ['exam_name', 'classname', 'subject_id', 'files', 'academic_year','academic_session_year']

    

class Gradeform(ModelForm):
    class Meta:
        model=Graderule
        fields=['grade_name','gpa','min_mark','max_mark']

class Scheduleform(ModelForm):
    class Meta:
        model=Schedule
        fields=['exam_name','class_name','subject_id','exam_date','start_time','end_time','academic_year']  


