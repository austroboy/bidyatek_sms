from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import StaffProfile,StudentProfile,StaffProfile
from core.models import Admission_Year,ClassConfig
from shared.models import CustomUser
from django.utils import timezone
from crucial.models import SMSUsage, Hostel
from core.models import PeriodConfig
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from datetime import datetime, time
import logging
logger = logging.getLogger('attendance')

class Holiday(models.Model): 
    name=models.CharField(max_length=50)
    holiday_date=models.DateField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.holiday_name)


class StudentAttendance(models.Model):
    name=models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='student_attend')
    status=models.BooleanField(default=False)
    attendance_date=models.DateField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_attend_create')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_attend_update')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)
    
class StudentAttendanceLog(models.Model):
    student_attendance = models.ForeignKey(StudentAttendance, on_delete=models.CASCADE, related_name='stu_attendance_logs')
    status = models.BooleanField()
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.student_attendance.name} - {'In' if self.status else 'Out'} at {self.changed_at}"
    
class HostelAttendance(models.Model): 
    name=models.ForeignKey(Hostel,on_delete=models.CASCADE,related_name='hostel_student_attend')
    status=models.BooleanField(default=False) 
    attendance_date=models.DateField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostel_student_attend_create')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostel_student_attend_update')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name.student_id.student_field.name)
    
class HostelAttendanceLog(models.Model):
    hostel_attendance = models.ForeignKey(HostelAttendance, on_delete=models.CASCADE, related_name='hostel_attendance_logs')
    status = models.BooleanField()
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.hostel_attendance.name} - {'In' if self.status else 'Out'} at {self.changed_at}"

class PeriodAttendance(models.Model):
    name=models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='period_student_attend')
    period_id=models.ForeignKey(PeriodConfig,on_delete=models.CASCADE,related_name='period_attend')
    status=models.BooleanField(default=False)
    attendance_date=models.DateField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='period_attend_create')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='period_attend_update')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)

    

# @receiver(post_save, sender=StudentAttendance)
# def notify_sms(sender, instance, created, **kwargs):
#     sms_limit_obj = SMSUsage.objects.filter(Msg_type='NONMASKING').first()
#     print(sms_limit_obj.total_sms)
#     if sms_limit_obj.total_sms<1:
#         print('SMS LIMIT OVER')
#     else:
#         token = "7167141059b264c433eba39b13b8ccb2257292797d"
#         greenweburl = "http://api.greenweb.com.bd/api.php"
#         name = instance.name.student_field.name
#         parent_mobile= instance.name.parent_id.phone_number
#         to= "+880"+ parent_mobile
#         now = timezone.now().strftime('%I:%M %p')
#         if created:
        
#             msg= "{} স্কুলে পৌঁছে গেছে, সময়ঃ {}.".format(name, now)
#             sms_limit_obj.total_sms -= 1
#             sms_limit_obj.save() 

#             # data = {'token':token, 
#             # 'to':to, 
#             # 'message':msg}  
    
#             # responses = requests.post(url = greenweburl, data = data) 

#             # response = responses.text 
            
#         else:
#             previous_attendance = StudentAttendance.objects.filter(
#                 name=instance.name,
#                 attendance_date=instance.attendance_date
#             ).first().status

#             if previous_attendance is True:
#                 msg= "{} স্কুল থেকে বের হয়েছে, সময়ঃ {} .".format(name, now)
#                 sms_limit_obj.total_sms -= 1
#                 sms_limit_obj.save()
#                 # data = {'token':token, 
#                 # 'to':to, 
#                 # 'message':msg} 
        
#                 # responses = requests.post(url = greenweburl, data = data) 

#                 # response = responses.text 
            

    
class StaffAttendance(models.Model):
    name=models.ForeignKey(StaffProfile,on_delete=models.CASCADE,related_name='staff_attend')
    status=models.BooleanField(default=False)
    attendance_date=models.DateField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_attend_create')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_attend_update')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    
class StaffAttendanceLog(models.Model):
    staff_attendance = models.ForeignKey(StaffAttendance, on_delete=models.CASCADE, related_name='staff_attendance_logs')
    status = models.BooleanField()
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.staff_attendance.name} - {'In' if self.status else 'Out'} at {self.changed_at}"


class LeaveQuota(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    leave_days_limit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    working_hour = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.group.name} Quota'

class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    is_special = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    start_hour = models.TimeField(null=True, blank=True)
    end_hour = models.TimeField(null=True, blank=True)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="eleavetype")
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', blank=True)
    leave_application= models.ImageField(upload_to="leave_application",null=True,blank=True)
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_leave_requests')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_leave_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee.name} - {self.start_date} to {self.end_date}'

    def is_hourly_leave(self):
        return self.start_hour is not None and self.end_hour is not None

    def calculate_leave_duration(self):
        """
        Calculate the duration of the leave for the specific employee.
        """
        if self.is_hourly_leave():
            start_datetime = datetime.combine(self.start_date, self.start_hour)
            end_datetime = datetime.combine(self.end_date, self.end_hour)
            duration = end_datetime - start_datetime
            total_hours = duration.total_seconds() / 3600
            # print(f"Employee: {self.employee.name}, Total hours: {total_hours}")
            return 0, total_hours
        else:
            duration = self.end_date - self.start_date
            total_days = duration.days + 1
            # print(f"Employee: {self.employee.name}, Total days: {total_days}")
            return total_days, 0

    