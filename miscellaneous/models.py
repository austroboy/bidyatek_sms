from django.db import models
from core.models import Admission_Year
from shared.models import CustomUser
from user.models import StudentProfile


class WeekendDay(models.Model):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES, unique=True)
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.get_day_display()
    
class Timing(models.Model):
    working_hour = models.IntegerField(default=8)
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        
        return f'Working Hour: {self.working_hour} | Academic Year: {self.academic_year}'

class Institute(models.Model): 
    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        DEACTIVE = 'Deactive', 'Deactive'

    class Gender(models.TextChoices):
        COMBINED = 'Combined', 'Combined'
        BOYS = 'Boys', 'Boys'
        GIRLS = 'Girls', 'Girls'

    institute_id = models.CharField(max_length=30, default=None)
    institute_logo = models.ImageField(null=True, blank=True, upload_to='image')
    signature = models.ImageField(null=True, blank=True, upload_to='image')
    institute_name = models.CharField(max_length=100, default=None)
    institute_gender_type = models.CharField(
        max_length=8, choices=Gender.choices, default=Gender.COMBINED
    )
    institute_eiin_no = models.CharField(max_length=50, null=True, blank=True, default=None)
    institute_email_address = models.CharField(max_length=100, null=True, blank=True, default=None)
    education_board_id = models.CharField(max_length=100, null=True, blank=True)
    education_division_id = models.CharField(max_length=100, null=True, blank=True)
    education_district_id = models.CharField(max_length=100, null=True, blank=True)
    education_thana_id = models.CharField(max_length=100, null=True, blank=True)
    headmaster_name = models.CharField(max_length=50, default=None)
    headmaster_mobile = models.CharField(max_length=15, default=None)
    incharge_manager = models.CharField(max_length=50, null=True, blank=True, default=None)
    incharge_manager_mobile = models.CharField(max_length=15, null=True, blank=True, default=None)
    incharge_manager_email = models.CharField(max_length=100, null=True, blank=True, default=None)
    institute_address = models.CharField(max_length=255, null=True, blank=True)
    institute_web = models.CharField(max_length=100, null=True, blank=True)
    institute_management_web = models.CharField(max_length=100, null=True, blank=True)
    institute_youtube = models.CharField(max_length=100, null=True, blank=True)
    institute_fb = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.institute_name

class Event(models.Model):
    title=models.CharField(max_length=100)
    start=models.DateTimeField(null=True,blank=True)
    end=models.DateTimeField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,blank=True, null=True,related_name='event_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class TestmonialSettings(models.Model):
    status=( 
        ('ACTIVE','ACTIVE'), 
        ('INACTIVE','INACTIVE')
    )
    header = models.CharField(max_length=50,null=True,blank=True)
    body =models.TextField(null=True,blank=True)
    subbody =models.TextField(null=True,blank=True)
    footer = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=10, choices=status,default='ACTIVE')
    signature_name = models.CharField(max_length=50,null=True,blank=True)
    head_master_signature = models.ImageField(upload_to='signature',null=True,blank=True)

    def __str__(self): 
        return (self.header) 
    
    class Meta:
        verbose_name_plural = "Testmonial Settings" 
    
class Testimonial(models.Model):
    student_id=models.ForeignKey(StudentProfile, on_delete=models.CASCADE,related_name='stu_tesimonial')
    serial = models.CharField(max_length=50,null=True,blank=True,unique=True)
    exam=models.CharField(max_length=50,null=True,blank=True)
    e_roll=models.CharField(max_length=20,null=True,blank=True)
    r_no=models.CharField(max_length=20,null=True,blank=True)
    exam_center =models.CharField(max_length=50,null=True,blank=True) 
    exam_held_date =models.DateField(max_length=50,null=True,blank=True)
    group_name=models.CharField(max_length=40,null=True,blank=True)
    session=models.CharField(max_length=20,null=True,blank=True)
    result=models.CharField(max_length=20,null=True,blank=True)
    issue_date=models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.serial:
            last_testimonial = Testimonial.objects.all().order_by('id').last()
            if last_testimonial and last_testimonial.serial and last_testimonial.serial.startswith('TM'):
                last_serial_no = last_testimonial.serial
            else:
                last_serial_no = 'TM0000'
            new_serial_no = 'TM' + str(int(last_serial_no[2:]) + 1).zfill(4)
            self.serial = new_serial_no
        super().save(*args, **kwargs)

    def __str__(self): 
        return str(self.student_id.student_field)
    
    
    
    
