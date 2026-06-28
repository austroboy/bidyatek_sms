from django.db import models
from core.models import StudentClass,Subject,Admission_Year,Mark_config,ClassConfig,SubjectConfig,AcademicSession,ClassGroupConfig
from user.models import StudentProfile,StaffProfile
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

class Examname(models.Model):
    name=models.CharField(max_length=40)
    start_date=models.DateField(null=True,blank=True)
    end_date=models.DateField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name + " " + self.academic_year.name
    class Meta:
        ordering = ['-id']
    
class ClassExam(models.Model):
    exam_name = models.ForeignKey(Examname, on_delete=models.CASCADE)
    class_name = models.ForeignKey(StudentClass,on_delete=models.CASCADE)  
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    
    def __str__(self):
        return f'{self.exam_name.name} - {self.class_name.name} ({self.start_date} to {self.end_date})'
    
class Examroom(models.Model):
    name=models.CharField(max_length=40)
    def __str__(self):
        return str(self.name)

class Graderule(models.Model):
    grade_name=models.CharField(max_length=2)
    gpa=models.FloatField()
    min_mark=models.IntegerField()
    max_mark=models.IntegerField()
    remarks= models.CharField(max_length=100,null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.gpa)
    
class Syllabus(models.Model):
    exam_name=models.ForeignKey(Examname,on_delete=models.CASCADE,related_name="student_routine" )
    classname=models.ForeignKey(ClassGroupConfig,on_delete=models.CASCADE)
    subject_id=models.ForeignKey(Subject,on_delete=models.CASCADE)
    files=models.FileField(upload_to='files',blank=True,null=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    academic_session_year = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__(self):
        return str(self.classname)

    class Meta:
        verbose_name_plural='Syllabus'


class Schedule(models.Model):
    exam_name=models.ForeignKey(Examname, on_delete=models.CASCADE)
    class_name=models.ForeignKey(ClassConfig,on_delete=models.CASCADE) 
    subject_id=models.ForeignKey(Subject,on_delete=models.CASCADE)
    exam_date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    exam_room=models.ForeignKey(Examroom,on_delete=models.CASCADE,null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__(self):
        return str(self.exam_name) 
    

class Forth_Sub(models.Model):
    Forth_TYPE = (
    ('COMPULSARY', 'COMPULSARY'),
    ('OPTIONAL', 'OPTIONAL'),
    )
    sub_conf_id = models.ForeignKey(SubjectConfig, on_delete= models.CASCADE, related_name="forth_sub")
    student_id= models.ForeignKey(StudentProfile, on_delete= models.SET_NULL, null=True, related_name="forth_stu_name")
    forth_type=models.CharField(max_length=12, choices=Forth_TYPE,null=True,blank=True)

    def __str__(self):
        return str(self.student_id.student_field.name + " - " + self.sub_conf_id.subject_id.name) + " - " + self.forth_type


class Subject_mark(models.Model):
    examname_id = models.ForeignKey(Examname, on_delete=models.CASCADE, related_name="subject_exam")
    student_id = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="student_mark")
    mark_id = models.ForeignKey(Mark_config, on_delete=models.SET_NULL, null=True, related_name="student_mark_conf")
    mark = models.FloatField(default=0)
    check_mark = models.BooleanField(default=False)
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.mark_id:
            raise ValidationError("Mark configuration cannot be null.")
        if self.mark > self.mark_id.mark:
            raise ValidationError("Subject mark is greater than the main mark.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.examname_id.name} {self.student_id.student_field.name}"

@receiver(post_save, sender=Subject_mark)
def update_student_result_on_mark_save(sender, instance, **kwargs):
    """
    Update StudentResult when a Subject_mark is saved and calculate the third mark if applicable.
    """
    student = instance.student_id
    exam = instance.examname_id
    academic_year = instance.academic_year

    student_result, created = StudentResult.objects.get_or_create(
        student=student,
        exam=exam,
        academic_year=academic_year,
    )

    student_result.calculate_result()
    student_result.save()

    try:
        subject_conf = instance.mark_id.subject_conf_id
    except Mark_config.DoesNotExist:
        return

    mark_configs = Mark_config.objects.filter(subject_conf_id=subject_conf)
    if mark_configs.count() != 3:
        return

    mark_config_list = list(mark_configs)

    student = instance.student_id
    exam = instance.examname_id

    existing_marks = Subject_mark.objects.filter(
        student_id=student,
        examname_id=exam,
        mark_id__in=mark_config_list
    )

    if existing_marks.count() != 2:
        return

    entered_config_ids = {m.mark_id.id for m in existing_marks}
    missing_config = None
    for config in mark_config_list:
        if config.id not in entered_config_ids:
            missing_config = config
            break

    if not missing_config:
        return  

    total_entered = sum(m.mark for m in existing_marks)
    total_possible_entered = sum(config.mark for config in mark_config_list if config.id in entered_config_ids)

    if total_possible_entered == 0:
        percentage = 0
    else:
        percentage = (total_entered / total_possible_entered) * 100

    third_mark_value = (percentage / 100) * missing_config.mark
    third_mark_value = round(third_mark_value, 2)
    third_mark_value = max(third_mark_value, 0)  
    third_mark_value = min(third_mark_value, missing_config.mark)  

    Subject_mark.objects.update_or_create(
        student_id=student,
        examname_id=exam,
        mark_id=missing_config,
        defaults={
            'mark': third_mark_value,
            'academic_year': academic_year
        }
    )








# @receiver(post_save, sender=Subject_mark)
# def update_student_result_on_mark_save(sender, instance, **kwargs):
#     """
#     Update StudentResult when a Subject_mark is saved.
#     """
#     student = instance.student_id
#     exam = instance.examname_id
#     academic_year = instance.academic_year

#     # Get or create the StudentResult for this student and exam
#     student_result, created = StudentResult.objects.get_or_create(
#         student=student,
#         exam=exam,
#         academic_year=academic_year,
#     )

#     # Recalculate the result
#     student_result.calculate_result()
#     student_result.save()

class StudentResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="exam_results")
    exam = models.ForeignKey(Examname, on_delete=models.CASCADE, related_name="student_results")
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    is_pass = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    fail_sub = models.IntegerField(null=True, blank=True)
    subjects_details = models.JSONField(default=dict)  # Stores JSON data
    gpa = models.FloatField(default=0.0)
    obtained_marks = models.FloatField(default=0.0)  # Add this field

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_result(self):
        """
        Calculate total marks, obtained marks, GPA, and pass/fail status.
        Updates the subjects_details JSON field.
        """
        # Initialize variables
        total_marks = 0
        obtained_marks = 0
        is_pass = True
        subjects_details = []
        fail_count = 0
        total_grade_points = 0  # Initialize total grade points
        graded_subject_count = 0  # Initialize count of graded subjects
        optional_grade_points = 0  # To calculate additional optional points

        # Get all marks for this student and exam
        subject_marks = Subject_mark.objects.filter(student_id=self.student, examname_id=self.exam)

        # Group marks by subject
        subject_grouped_marks = {}
        for subject_mark in subject_marks:
            subject_conf = subject_mark.mark_id.subject_conf_id
            if subject_conf not in subject_grouped_marks:
                subject_grouped_marks[subject_conf] = []
            subject_grouped_marks[subject_conf].append(subject_mark)

        # Process each subject
        for subject_conf, marks in subject_grouped_marks.items():
            subject_total_marks = subject_conf.mark  # Specific total marks for this subject
            subject_obtained_marks = 0
            subject_is_pass = True

            # Check if the subject is optional
            forth_sub = Forth_Sub.objects.filter(student_id=self.student, sub_conf_id=subject_conf).first()
            is_optional = forth_sub and forth_sub.forth_type == "OPTIONAL"

            # Check all mark_type_id for the subject
            for mark in marks:
                mark_config = mark.mark_id
                if not mark_config:  # Skip if mark_config is None
                    continue

                # Check if this mark is passing
                if mark.mark < mark_config.pass_mark:
                    subject_is_pass = False

                subject_obtained_marks += mark.mark

            # Add to total marks and obtained marks only if all marks for this subject are passing
            total_marks += subject_total_marks
            if subject_is_pass:
                obtained_marks += subject_obtained_marks
            else:
                fail_count += 1
                if not forth_sub or forth_sub.forth_type == 'COMPULSARY':
                    is_pass = False

            # Add subject details to JSON
            percentage = (subject_obtained_marks / subject_total_marks) * 100 if subject_total_marks > 0 else 0
            grade = None
            remarks = None
            grading_rules = Graderule.objects.all()

            if subject_is_pass:
                for rule in grading_rules:
                    if rule.min_mark <= percentage <= rule.max_mark:
                        grade = rule.gpa
                        remarks = rule.remarks
                        break
            else:
                # Set grade to 0 for failed subjects
                grade = 0
                remarks = "Failed"

            if is_optional:
                # Collect optional points but do not add them to total_grade_points yet
                if grade == 5:
                    optional_grade_points += 2
                elif grade == 4:
                    optional_grade_points += 1
            else:
                # Regular subject processing
                if grade is not None:
                    total_grade_points += grade
                    graded_subject_count += 1

            subjects_details.append({
                "subject_name": subject_conf.subject_id.name,
                "subject_Serial": subject_conf.subject_Serial,
                "subject_marge": subject_conf.subject_marge,
                "subject_type": subject_conf.subject_type,
                "total_marks": subject_total_marks,
                "obtained_marks": subject_obtained_marks if subject_is_pass else 0,
                "percentage": percentage,
                "grade": grade,
                "remarks": remarks,
                "is_pass": subject_is_pass,
                "is_optional": is_optional
            })

        self.total_marks = total_marks
        self.obtained_marks = obtained_marks
        self.is_pass = is_pass
        self.fail_sub = fail_count
        self.subjects_details = subjects_details

        # Calculate base GPA across all subjects
        base_gpa = total_grade_points / graded_subject_count if graded_subject_count > 0 else 0

        # Add optional points only if the base GPA is less than 5
        self.gpa = min(base_gpa + optional_grade_points, 5)

        # Add overall remarks
        if graded_subject_count > 0:
            percentage = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
            for rule in grading_rules:
                if rule.min_mark <= percentage <= rule.max_mark:
                    self.remarks = rule.remarks
                    break


    def save(self, *args, **kwargs):
        self.calculate_result()
        super().save(*args, **kwargs)
