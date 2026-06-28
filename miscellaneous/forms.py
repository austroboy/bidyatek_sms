from django import forms
from .models import *

class InstituteForm(forms.ModelForm):
    class Meta:
        model = Institute
        fields = '__all__'

class EventFrom(forms.ModelForm):
    class Meta:
        model =Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].disabled = True
        
class TestmonialSettingsForm(forms.ModelForm):
    class Meta:
        model = TestmonialSettings
        fields = ['header', 'body', 'subbody', 'footer', 'status', 'signature_name', 'head_master_signature']



class WeekendDayForm(forms.ModelForm):
    class Meta:
        model = WeekendDay
        fields = ['day','academic_year']
       

class TimingForm(forms.ModelForm):
    class Meta:
        model = Timing
        fields = ['working_hour', 'academic_year']
       