from django.forms import ModelForm
from .models import *

class StudentAttendForm(ModelForm):
    class Meta:
        model=StudentAttendance
        fields='__all__'


class LeaveTypeForm(ModelForm):
    class Meta:
        model=LeaveType
        fields='__all__'

class LeaveRequestForm(ModelForm):
    class Meta:
        model = LeaveRequest
        fields = '__all__'  # Or specify fields explicitly if needed

    def __init__(self, *args, **kwargs):
        user_list = kwargs.pop('user_list', None)
        super().__init__(*args, **kwargs)
        
        if user_list:
            self.fields['employee'].queryset = CustomUser.objects.filter(id__in=[user.id for user in user_list])

class Holidayform(ModelForm):
    class Meta:
        model=Holiday
        fields='__all__'

class LeaveQuotaform(ModelForm):
    class Meta:
        model=LeaveQuota
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(LeaveQuotaform, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.exclude(name='parent')
        self.fields['working_hour'].required = False
