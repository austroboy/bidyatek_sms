from django.db import models
from datetime import datetime

# Create your models here.

def get_current_year():
    """Returns the current year as a string."""
    return str(datetime.now().year)

class Admission_Year(models.Model):
    name = models.CharField(
        max_length=4, 
        default=get_current_year  
    )
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__ (self):
        return self.name
    

class AcademicSession(models.Model):
    start_year = models.CharField(max_length=4)
    end_year = models.CharField(max_length=4)  
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.start_year}-{self.end_year}"
    

class StudentClass(models.Model):
    name=models.CharField(max_length=30)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self):
        return self.name
    class Meta:
        verbose_name_plural = "StudentClass"

class Subject(models.Model):
    name=models.CharField(max_length=30)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self):
        return self.name
    
class StudentSection(models.Model):
    name=models.CharField(max_length=30)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self):
        return self.name
    
class StudentShift(models.Model):
    name=models.CharField(max_length=30)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self):
        return self.name
    
class StuGroup(models.Model):
    name=models.CharField(max_length=40)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 

class Period(models.Model):
    name=models.CharField(max_length=30)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self): 
        return self.name  
        

class ClassGroupConfig(models.Model):
    class_id = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='config_class')
    group_id = models.ForeignKey(StuGroup, on_delete=models.SET_NULL, related_name='config_group', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Safely handle missing or invalid related objects
        class_name = self.class_id.name if self.class_id else " "
        group_name = self.group_id.name if self.group_id else " "
        return f"{class_name} {group_name}"

class ClassConfig(models.Model):
    class_group_id = models.ForeignKey(ClassGroupConfig, on_delete=models.CASCADE, related_name='config_class_group')
    section_id = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='config_section')
    shift_id = models.ForeignKey(StudentShift, null=True ,blank=True, on_delete=models.SET_NULL, related_name='shift_section')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        class_name = self.class_group_id.class_id.name
        shift_name = self.shift_id.name if self.shift_id else ""
        section_name = self.section_id.name if self.section_id else ""
        group_name = self.class_group_id.group_id.name if self.class_group_id.group_id else ""
        
        if group_name and shift_name and section_name:
            return f"{class_name} {group_name} {section_name} {shift_name}"
        elif shift_name and section_name:
            return f"{class_name} {section_name} {shift_name}"
        elif group_name and section_name:
            return f"{class_name} {group_name} {section_name}"
        elif class_name and section_name:
            return f"{class_name} {section_name}"
        
        else:
            return f"{class_name} {group_name}"
        
    
class PeriodConfig(models.Model):
    class_id=models.ForeignKey(ClassConfig,on_delete=models.CASCADE,related_name='config_class_period')
    period_id=models.ForeignKey(Period,on_delete=models.CASCADE,related_name='config_period')
    start_time=models.TimeField()
    end_time=models.TimeField()
    break_time= models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self):
        return self.class_id.class_group_id.class_id.name + " " + (self.class_id.section_id.name if self.class_id.section_id else "")   + " " + self.period_id.name 
    

class SubjectAssign(models.Model):
    class_id = models.ForeignKey(ClassGroupConfig, on_delete=models.CASCADE, related_name='assign_class')
    subjects = models.ManyToManyField(Subject) 
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        subjects_str = ', '.join(str(subject) for subject in self.subjects.all())
        return f"{self.class_id.class_id.name} - Subjects: {subjects_str}"
    

class SubjectConfig(models.Model): 
    SUBJECT_TYPE = (
    ('COMPULSARY', 'COMPULSARY'),
    ('CHOOSABLE', 'CHOOSABLE'),
    ('Group Based', 'Group Based'),
    ('Uncountable', 'Uncountable'),
    )
    class_id= models.ForeignKey(ClassGroupConfig,on_delete=models.CASCADE, related_name='class_conf')
    subject_id= models.ForeignKey(Subject,on_delete=models.CASCADE,null=True,blank=True, related_name='subject_conf')
    subject_Serial= models.IntegerField(null=True,blank=True,default=0)
    subject_marge= models.IntegerField(null=True,blank=True,default=0)
    subject_type=models.CharField(max_length=12, choices=SUBJECT_TYPE,null=True,blank=True, default="COMPULSARY")
    mark= models.IntegerField(null=True,blank=True,default=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
     
    def __str__(self):
         
        class_name = self.class_id if self.class_id else "Unknown Class"
        subject_name = self.subject_id.name if self.subject_id else "Unknown Subject"
        
        return f"{class_name} {subject_name} "
    
    class Meta:
        ordering = ['subject_Serial']
    

class Mark_type(models.Model):
    name=models.CharField(max_length=30)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__ (self): 
        return self.name
    
class Mark_config(models.Model):
    class_id= models.ForeignKey(ClassGroupConfig,on_delete=models.CASCADE, related_name='mc_config')
    subject_conf_id=models.ForeignKey(SubjectConfig,on_delete=models.CASCADE,related_name="ms_config")
    mark_type_id=models.ForeignKey(Mark_type,on_delete=models.CASCADE,related_name="mt_config")
    mark=models.FloatField(default=0, null=True,blank=True)
    pass_mark=models.FloatField(default=0, null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True) 

    def __str__(self):
        class_name = str(self.subject_conf_id.class_id.class_id.name) if self.subject_conf_id.class_id.class_id else "Unknown Class"
        group_name = str(self.subject_conf_id.class_id.group_id.name) if self.subject_conf_id.class_id.group_id else "Unknown Group"
        subject_name = str(self.subject_conf_id.subject_id.name) if self.subject_conf_id.subject_id else "Unknown Subject"
        mark_type = str(self.mark_type_id.name) if self.mark_type_id else "Unknown Mark Type"

        return f"{class_name} {group_name} {subject_name} {mark_type}"

    