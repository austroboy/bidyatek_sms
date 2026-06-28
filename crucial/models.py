from django.db import models
from core.models import ClassConfig,PeriodConfig,Subject,Admission_Year,AcademicSession
from user.models import Student,StudentProfile,StaffProfile
from shared.models import CustomUser
from django.utils import timezone
from django.contrib.auth.models import Group
from datetime import date
from django.db.models import Sum,DecimalField
from django.db.models.signals import post_save, pre_delete,post_delete,pre_save
from django.dispatch import receiver
from decimal import Decimal
from user.models import CustomUser
from core.models import StudentClass,SubjectAssign,StuGroup,ClassGroupConfig
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from accounting.models import *
from django.utils.timezone import now
import logging
from django.db import IntegrityError


class TeacherSubjectAssign(models.Model):
    teacher_id = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='sub_assign_teacher')
    subject_assigns = models.ManyToManyField(Subject, related_name='teacher_sub_assignments')
    class_assigns = models.ManyToManyField(ClassConfig, related_name='teacher_class_assignments')
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        subject_assigns_str = ', '.join(str(assign) for assign in self.subject_assigns.all())
        return f"{self.teacher_id.staff_field.name} - Subject Assignments: {subject_assigns_str}" 


class Routine(models.Model): 
    DAYS_OF_WEEK = (
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'), 
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),       
    )
    class_id=models.ForeignKey(ClassConfig,on_delete=models.CASCADE,related_name="class_routine")
    period_id=models.ForeignKey(PeriodConfig,on_delete=models.SET_NULL,null=True,related_name="period_routine")
    day_name=models.CharField(max_length=10,choices=DAYS_OF_WEEK)
    subject_id=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='subject_routine')
    teacher_name=models.ForeignKey(StaffProfile,on_delete=models.SET_NULL,null=True,related_name='teacher_routine')
    note= models.CharField(max_length=150,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        # Example fix - adjust based on your actual code
        if self.some_field and self.some_field.class_group_id:
            return f"{self.some_field.class_group_id.name}"
        elif self.some_field:
            return f"ID: {self.id} - Class field exists but no class_group"
        else:
            return f"ID: {self.id}"

class Homework(models.Model):
    subject_id=models.ForeignKey(Subject,on_delete=models.CASCADE)
    class_id=models.ForeignKey(ClassConfig,on_delete=models.CASCADE)
    homework_title = models.CharField(max_length=150)
    homework_description = models.TextField()
    homework_date = models.DateField()
    file_attachment=models.FileField(upload_to ='Homework/')
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.homework_title

class HomeworkSubmission(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    attachment_url = models.ImageField(upload_to ='Homework/')
    # status = models.CharField(max_length=20, choices=[('submitted', 'Submitted'), ('graded', 'Graded')], default='submitted')
    # score = models.PositiveIntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class Hostel_package(models.Model):
    package_name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package_name
    
    class Meta:
        verbose_name_plural = "Hostel Package"


class Hostel(models.Model):
    status = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    )
    hostel_package = models.ForeignKey(Hostel_package, on_delete=models.SET_NULL, null=True)
    student_id = models.ForeignKey(StudentProfile, on_delete=models.PROTECT, related_name="hostel_student")
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hostel fee for: {self.student_id} - {self.hostel_package}"


class Tution_package(models.Model):
    package_name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package_name
    
    class Meta:
        verbose_name_plural = "Tution Package"


class Tution(models.Model):
    status = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    )
    tution_package = models.ForeignKey(Tution_package, on_delete=models.SET_NULL, null=True)
    student_id = models.ForeignKey(StudentProfile, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tution fee for: {self.student_id} - {self.tution_package}"
    
class Transport_package(models.Model):
    package_name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package_name

    class Meta:
        verbose_name_plural = "Transport Package"

class Transport(models.Model):
    status = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    )
    transport_package = models.ForeignKey(Transport_package, on_delete=models.SET_NULL, null=True)
    student_id = models.ForeignKey(StudentProfile, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transport fee for: {self.student_id} - {self.transport_package}"
    
class Fee_month(models.Model):
    name = models.CharField(max_length=9)
    def __str__(self):
        return self.name
    


class Feetype(models.Model):
    status=(
        ('Active','Active'),
        ('Inactive','Inactive')
    )
    schedule = (
        ('Annually', 'Annually'),
        ('Bi-Annually', 'Bi-Annually'),
        ('Tri-Annually', 'Tri-Annually'),
        ('Quarterly', 'Quarterly'), 
        ('Two-Monthly', 'Two-Monthly'),
        ('Monthly', 'Monthly')
    )
    class Version(models.TextChoices):
        BANGLA = 'Bangla',
        ENGLISH = 'English',
    
    version = models.CharField(
    max_length=8,
    choices=Version.choices,
    null=True,  
    blank=True  
    )
    fee_head = models.ForeignKey('FeeHead', on_delete=models.CASCADE, related_name='fee_types')
    is_hostel_fee=models.BooleanField(default=False)
    is_transport_fee=models.BooleanField(default=False)
    is_coaching_fee=models.BooleanField(default=False)
    late_fee_percentage = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    fee_Schedule = models.CharField(max_length=20, choices=schedule)
    status= models.CharField(max_length=20, choices=status, default='Active')
    description= models.CharField(max_length=50,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='fees_type_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='fees_type_updator')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self):
        return self.fee_head.name
    
    
    def get_number_of_months(self):
        schedule_to_months = {
            'Annually': 1,
            'Bi-Annually': 2,
            'Tri-Annually': 3,
            'Quarterly': 4,
            'Monthly': 12,
            'Two-Monthly': 6
        }
        return schedule_to_months.get(self.fee_Schedule, 0)
    
class Waiver(models.Model):
    student_id = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="student_waiver")
    waiver_amount = models.IntegerField() 
    fee_types = models.ManyToManyField(Feetype, related_name='waivers')  # Many-to-many relationship
    academic_year = models.ForeignKey(Admission_Year, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='waiver_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Waiver for {self.student_id} - {self.waiver_amount}"

class Fee_package(models.Model):
    student_class = models.ForeignKey(ClassGroupConfig, on_delete=models.CASCADE, related_name='fees_amount_class')
    fees_type= models.ForeignKey(Feetype, on_delete=models.CASCADE,related_name='fees_name_type_amount')
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='fees_amount_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='fees_amount_updator')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__ (self):
        return str(self.student_class) + " "+ str(self.fees_type) +" " +str(self.amount)
    
    
class Fees_name(models.Model):
    status=(
        ('Active','Active'),
        ('Inactive','Inactive')
    )
    fees_title = models.CharField(max_length=50)
    fees_type= models.ForeignKey(Feetype, on_delete=models.CASCADE, related_name='fees_name_type')
    fee_amount_id = models.ForeignKey(Fee_package, on_delete=models.CASCADE, related_name='fees_name_amount',null=True,blank=True)
    month = models.ForeignKey(Fee_month, on_delete=models.CASCADE , related_name='fees_name_monthwise')
    status= models.CharField(max_length=20, choices=status, default='Active')
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='fees_name_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='fees_name_updator')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_from_fee_amount(cls, fees_type, month, start_date, end_date, user, academic_year, fee_amount=None):
        fees_title_parts = [month.name, fees_type.fee_head.name]

        if fee_amount:
            class_name = fee_amount.student_class.class_id.name if fee_amount.student_class.class_id else "Unknown Class"
            group_name = fee_amount.student_class.group_id.name if fee_amount.student_class.group_id else ""
            if group_name:
                fees_title_parts.append(f"{class_name} - {group_name}")
            else:
                fees_title_parts.append(f"{class_name}")
        
        fees_title = " - ".join(fees_title_parts)

        fees_name_instance = cls(
            fees_title=fees_title,
            fees_type=fees_type,
            fee_amount_id=fee_amount,
            month=month,
            startdate=start_date,
            enddate=end_date,
            academic_year=academic_year,
            created_by=user,
            updated_by=user
        )
        fees_name_instance.save()
        return fees_name_instance

    def __str__(self):
        return self.fees_title


class PartialPayment(models.Model):
    fee = models.ForeignKey('Fees', on_delete=models.CASCADE, related_name='partial_payments')
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"Payment of {self.amount} on {self.payment_date} for fee {self.fee.id}"


class Fees(models.Model):
    status=( 
        ('paid','paid'),
        ('unpaid','unpaid'),
        ('partial','partial')
    )

    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online Payment'),
        ('cash', 'Cash Payment'),
        ('cheque', 'Cheque Payment'),
    )

    student_id=models.ForeignKey(StudentProfile,on_delete=models.PROTECT) 
    feetype_id=models.ForeignKey(Fees_name,on_delete=models.SET_NULL,null=True)
    transaction_no=models.CharField(max_length=20,null=True,blank=True,unique=True)
    amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    late_amount = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    status=models.CharField(max_length=7,choices=status,default='unpaid')
    is_enable=models.BooleanField(default=True)
    month_id = models.ForeignKey(Fee_month, on_delete=models.CASCADE , related_name='fees_monthwise' )
    description=models.CharField(max_length=50, null=True,blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, null=True, blank=True)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    fees_record= models.JSONField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.DO_NOTHING,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='fees_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.transaction_no:
            last_fee = Fees.objects.all().order_by('id').last()
            last_transaction_no = last_fee.transaction_no if last_fee else 'FEE0001'
            new_transaction_no = 'FEE' + str(int(last_transaction_no[3:]) + 1).zfill(4)
            self.transaction_no = new_transaction_no
        super().save(*args, **kwargs)


    def record_payment(self, amount, created_by):
        """
        Record a payment for a fee and create a corresponding Receive entry.
        """
        # Step 1: Record the partial payment
        PartialPayment.objects.create(fee=self, amount=amount, created_by=created_by)

        # Step 2: Update the fee status based on the total payments
        self.update_fee_status()

        # Step 3: Create a Receive entry
        Receive.objects.create(
            received_from=self.student_id,  
            fee_head=self.feetype_id,      
            amount=amount,
            date=timezone.now().date(),
            total_amount=amount,
            voucher_no=f"FEE-{self.transaction_no}",
            description=f"Payment for {self.feetype_id.fees_title}",
        )



    def calculate_late_fee(self):
        today = date.today()
        if self.status in ['unpaid', 'partial'] and self.feetype_id and self.feetype_id.enddate:
            if self.feetype_id.enddate < today:
                late_fee_percentage = self.feetype_id.fees_type.late_fee_percentage
                late_fee = (late_fee_percentage / 100) * self.amount
                return late_fee
        return Decimal('0.00')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 

        # If late fee exists, create a ledger entry
        if self.late_amount > Decimal('0.00'):
            ledger_name = f"late_fee_{self.student_id.student_field.user_id}"
            ledger_category = LedgerCategory.objects.filter(name=LedgerCategory.OTHERS_INCOME).first()

            if not Ledger.objects.filter(name=ledger_name).exists():
                Ledger.objects.create(
                    name=ledger_name,
                    category=ledger_category,
                    note=f"Late fee ledger for student ID {self.student_id.student_field.user_id}",
                    created_at=timezone.now()
                )
         
    def total_fee(self):
        total_fee = self.amount
        late_fee = self.calculate_late_fee()
        if late_fee:
            total_fee += late_fee
        else:
            total_fee += self.late_amount
        return total_fee
    
    def total_fee_after_discount(self):
        total_fee = self.total_fee() - self.discount_amount
        return max(total_fee, 0)
    
    def total_paid_amount(self):
        total_paid = self.partial_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        return total_paid
    
    def total_netTotal(self):
        total_paid = Decimal('0.00')
        if self.status == 'partial':
            total_paid = self.total_paid_amount()
            
        total_fee = Decimal('0.00')
        if self.status == 'paid':
            total_fee = self.total_fee() - self.discount_amount
            
        nettotal_fee = total_fee + total_paid

        return max(nettotal_fee, 0)
    
    def total_fee_after_partial_payments(self):
        if self.status == 'partial':
            total_fee = self.late_amount + self.amount - self.discount_amount
        else: 
            total_fee = self.calculate_late_fee() + self.amount - self.discount_amount
        total_paid = self.total_paid_amount()
        remaining_fee = total_fee - total_paid
        return max(remaining_fee, 0)
    

    def update_fee_status(self):
        total_paid = Decimal(self.total_paid_amount())
        
        late_fee = Decimal(self.calculate_late_fee() or self.late_amount)
        amount = Decimal(self.amount or '0.00')
        discount_amount = Decimal(self.discount_amount or '0.00')
        
        total_fee = late_fee + amount - discount_amount
        
        
        if total_paid == total_fee:
            self.status = 'paid'
           
        elif total_paid > Decimal('0.00'):
            self.status = 'partial'
            
        else:
            self.status = 'unpaid'
           

        self.save(update_fields=['status'])


    def record_payment(self, amount, created_by):
        PartialPayment.objects.create(fee=self, amount=amount, created_by=created_by)
        self.update_fee_status()
        
    def __str__ (self):
            return str(self.student_id) +'-'+ str(self.feetype_id)
    
    class Meta:
        verbose_name_plural = "Fees"

# Fee Head model for unique fee categories
class FeeHead(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
logger = logging.getLogger(__name__)
@receiver(post_save, sender=FeeHead)
def create_ledger_for_feehead(sender, instance, created, **kwargs):
    if created:
        try:
            ledger_category = LedgerCategory.objects.get(name='Income')
            
            Ledger.objects.update_or_create(
                category=ledger_category,
                name=f"{instance.name} Income",
                defaults={
                    'code': f"INC-{instance.id:03d}",
                    'balance_type': 'Credit',
                    'description': f"Automatically created for FeeHead: {instance.name}",
                    'is_active': True,
                    'opening_balance': 0.00
                }
            )
            
        except LedgerCategory.DoesNotExist:
            logger.error(f"Income category not found. Create it first in accounting setup.")
            
        except IntegrityError as e:
            logger.error(f"Ledger creation failed for {instance.name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error creating ledger: {str(e)}")
      
            
# Fee Sub Head model for subcategories under Fee Head
class FeeSubHead(models.Model):
    head = models.ForeignKey(FeeHead, on_delete=models.CASCADE, related_name='sub_heads')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.head.name} - {self.name}"

# Configuration linking Fee Head and Sub Head
class FeeSubHeadConfig(models.Model):
    head = models.ForeignKey(FeeHead, on_delete=models.CASCADE, related_name='configurations')
    sub_heads = models.ManyToManyField(FeeSubHead, related_name='configurations')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.head.name} -> {self.sub_head.name}"

# Configuration to map Fee Head to Ledger
# class FeeHeadLedgerConfig(models.Model):
#     head = models.ForeignKey(FeeHead, on_delete=models.CASCADE, related_name='ledger_configurations')
#     ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='fee_head_ledger')
#     is_active = models.BooleanField(default=True)
#     created_at=models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.head.name} -> {self.ledger.name}"

# # Add predefined ledger names under "Others Income" category
# @receiver(post_save, sender=FeeHead)
# def create_ledger_for_feehead(sender, instance, created, **kwargs):
#     if created:
#         try:
#             # Get or create Income category
#             category, _ = LedgerCategory.objects.get_or_create(
#                 name='Income',
#                 defaults={'code': 'INCOME', 'description': 'Income accounts'}
#             )
            
#             # Create main ledger
#             main_ledger, _ = Ledger.objects.update_or_create(
#                 category=category,
#                 name=f"{instance.name} Income",
#                 defaults={
#                     'code': f"INC-{instance.id:03d}",
#                     'balance_type': 'Credit',
#                     'is_active': True,
#                     'description': f"Main income account for {instance.name}"
#                 }
#             )
            
#             # Create sub-ledgers if needed
#             if instance.name == "Tuition Fee":
#                 sub_ledgers = [
#                     ("TUI-001", "Tuition Fees"),
#                     ("BK-001", "Book Charges"),
#                     ("ICT-001", "ICT Fees"),
#                     ("SCM-001", "Sports Culture And Milad"),
#                     ("CLUB-001", "Club Scout"),
#                     ("SAFE-001", "Safety"),
#                     ("MAG-001", "Magazine"),
#                     ("ID-001", "ID Card"),
#                     ("LIB-001", "Library"),
#                     ("SEM-001", "Semester Fees"),
#                     ("GEN-001", "Generator"),
#                     ("BADGE-001", "Badge"),
#                     ("EXT-001", "Extension Fee")
#                 ]
                
#                 for code, name in sub_ledgers:
#                     Ledger.objects.update_or_create(
#                         category=category,
#                         name=name,
#                         defaults={
#                             'code': code,
#                             'balance_type': 'Credit',
#                             'is_active': True,
#                             'description': f"Sub-account of {instance.name} Income"
#                         }
#                     )
                    
#         except Exception as e:
#             logger.error(f"Error creating ledgers for {instance.name}: {str(e)}")
            
#Fees model close ######################################################


class MainBalance(models.Model):
    balance = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__(self):
        return f"Main Balance: {self.balance}"
    
class BalanceStatement(models.Model):
    balance_change = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    statement = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.statement

class IncomeHead(models.Model): 
    incometype=models.CharField(max_length=100)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__ (self):
        return self.incometype
    
class IncomeitemList(models.Model):
    incometype_id=models.ForeignKey(IncomeHead,on_delete=models.SET_NULL,null=True)
    name=models.CharField(max_length=100,null=True,blank=True)
    invoice_number=models.CharField(max_length=100,null=True,blank=True)
    income_date= models.DateField(null=True,blank=True)
    amount=models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    attach_doc=models.ImageField(upload_to="income",null=True,blank=True)
    description=models.CharField(max_length=100,null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='income_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__ (self):
        return str(self.incometype_id) + " " + (self.name)

@receiver(post_save, sender=IncomeitemList)
def update_main_balance_income(sender, instance, created, **kwargs):
    if created:
        main_balance = MainBalance.objects.first()
        main_balance.balance += instance.amount
        main_balance.save()
        # Create a statement for the increase in balance
        BalanceStatement.objects.create(
            balance_change=instance.amount,
            statement=f"Income: {instance.amount} added to Main Balance. New balance: {main_balance.balance}"
        )

@receiver(pre_delete, sender=IncomeitemList)
def reverse_main_balance_income(sender, instance, **kwargs):
    main_balance = MainBalance.objects.first()
    main_balance.balance -= instance.amount
    main_balance.save()
    # Create a statement for the decrease in balance
    BalanceStatement.objects.create(
        balance_change=-instance.amount,
        statement=f"Income: {instance.amount} removed from Main Balance. New balance: {main_balance.balance}"
    )


class ExpenseHead(models.Model):
    expensetype=models.CharField(max_length=100)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__ (self):
        return self.expensetype

class Expenseitemlist(models.Model):
    expensetype_id=models.ForeignKey(ExpenseHead,on_delete=models.SET_NULL,null=True)
    name=models.CharField(max_length=100,null=True,blank=True)
    transaction_no=models.CharField(max_length=100,null=True,blank=True)
    amount=models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    expense_date= models.DateField(null=True,blank=True)
    employee_id = models.CharField(max_length=50,null=True,blank=True)
    attach_doc = models.ImageField(upload_to="expense",null=True,blank=True)
    description=models.CharField(max_length=100,null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='expense_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__ (self):
        return str(self.expensetype_id) + " " + (self.name)
    
@receiver(post_save, sender=Expenseitemlist)
def update_main_balance_expense(sender, instance, created, **kwargs):
    if created:
        main_balance = MainBalance.objects.first()
        main_balance.balance = main_balance.balance - instance.amount 
        main_balance.save()
        BalanceStatement.objects.create(
            balance_change=-instance.amount,
            statement=f"Expense: {instance.amount} deducted from Main Balance. New balance: {main_balance.balance}"
        )

@receiver(pre_delete, sender=Expenseitemlist)
def reverse_main_balance_expense(sender, instance, **kwargs):
    main_balance = MainBalance.objects.first()
    main_balance.balance += instance.amount
    main_balance.save()
    BalanceStatement.objects.create(
        balance_change=instance.amount,
        statement=f"Expense: {instance.amount} added back to Main Balance. New balance: {main_balance.balance}"
    )
    
class Withdraw(models.Model):
    amount=models.DecimalField(max_digits=22, decimal_places=2, default=Decimal('0.00'))
    received_by=models.CharField(max_length=100,null=True,blank=True)
    note=models.CharField(max_length=100,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='withdraw_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    def __str__ (self):
        return str(self.received_by)
    
@receiver(post_save, sender=Withdraw)
def update_main_balance_withdraw(sender, instance, created, **kwargs):
    if created:
        main_balance = MainBalance.objects.first()
        main_balance.balance -= instance.amount
        main_balance.save()
        BalanceStatement.objects.create(
            balance_change=-instance.amount,
            statement=f"Withdrawal: {instance.amount} deducted from Main Balance. New balance: {main_balance.balance}"
        )

@receiver(pre_delete, sender=Withdraw)
def reverse_main_balance_withdraw(sender, instance, **kwargs):
    main_balance = MainBalance.objects.first()
    main_balance.balance += instance.amount
    main_balance.save()
    BalanceStatement.objects.create(
        balance_change=instance.amount,
        statement=f"Withdrawal: {instance.amount} added back to Main Balance. New balance: {main_balance.balance}"
    )

class Addition_type(models.Model):
    addition_type = models.CharField(max_length=50)
    is_every_month = models.BooleanField(default=True)
    def __str__(self):
        return self.addition_type

class Addition(models.Model):
    addition_type_id = models.ForeignKey(Addition_type, on_delete=models.CASCADE)
    employee_id = models.ForeignKey(StaffProfile, on_delete=models.PROTECT, related_name='salary_addition')
    amount = models.FloatField()
    date = models.DateField()

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")

    def __str__(self):
        return f" {self.addition_type_id.addition_type} - {self.amount}"
    
class Deduction_type(models.Model):
    deduction_type = models.CharField(max_length=50)
    is_every_month = models.BooleanField(default=True)
    def __str__(self):
        return self.deduction_type

class Deduction(models.Model):
    deduction_type_id = models.ForeignKey(Deduction_type, on_delete=models.CASCADE)
    employee_id = models.ForeignKey(StaffProfile, on_delete=models.PROTECT, related_name='salary_deduction')
    amount = models.FloatField()
    date = models.DateField()

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")
        
    def __str__(self):
        return f"{self.deduction_type_id.deduction_type} - {self.amount}"


class SalaryConfiguration(models.Model):
    employee = models.ForeignKey(StaffProfile, on_delete=models.PROTECT, related_name='salary_conf')
    basic_salary = models.FloatField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='salary_conf_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee.staff_field.name

    def calculate_additions(self):
        
        return Addition.objects.filter(
            employee_id=self.employee,
            addition_type_id__is_every_month=True  # Filtering by is_every_month=True
        ).aggregate(Sum('amount'))['amount__sum'] or 0

    def calculate_deductions(self):
        
        return Deduction.objects.filter(
            employee_id=self.employee,
            deduction_type_id__is_every_month=True  # Filtering by is_every_month=True
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    def calculate_salary_increment(self):
        """
        Calculates the total increment applicable based on increments that are effective.
        """
        increments = SalaryIncrement.objects.filter(
            employee=self.employee,
            effective_date__lte=now().date()
        ).order_by('effective_date')

        total_increment = 0
        for increment in increments:
            if increment.is_percentage:
                total_increment += (self.basic_salary * (increment.increment_amount / 100))
            else:
                total_increment += increment.increment_amount

        return round(total_increment, 2)

    def apply_salary_increment(self, salary):
        
        increments = SalaryIncrement.objects.filter(
            employee=self.employee, effective_date__lte=now().date()
        ).order_by('effective_date')

        for increment in increments:
            salary = increment.apply_increment(salary)

        return salary

    def total_salary(self):
     
        total = self.basic_salary
        total += self.calculate_additions() 
        total -= self.calculate_deductions() 
        total = self.apply_salary_increment(total) 

        return round(total, 2)


class SalaryProcess(models.Model):
    MONTH_CHOICES = [
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

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('mfs', 'Mobile Financial Service'),
    ]

    status = (
        ('paid', 'paid'),
        ('unpaid', 'unpaid'),
        ('partial', 'partial'),
    )
    employee_salary = models.ForeignKey(SalaryConfiguration, on_delete=models.PROTECT, related_name='employee_salary')
    salary_month = models.CharField(max_length=10, choices=MONTH_CHOICES)
    total_salary = models.FloatField(null=True, blank=True)
    salary_status = models.CharField(max_length=10, choices=status, default="unpaid")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    transaction_no = models.CharField(max_length=20, null=True, blank=True, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_record= models.JSONField(null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='salary_pro_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_amount = models.FloatField(null=True, blank=True, default=0)

    def __str__(self):
        return self.employee_salary.employee.staff_field.name + " - " + str(self.total_salary)


class AdvanceSalaryPayment(models.Model):
    employee = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()
    paid_status = models.BooleanField(default=False)
    remarks = models.TextField(null=True, blank=True)

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")
 
    def __str__(self):
        return f"{self.employee.staff_field.name} - {self.amount} - {self.date}"

class SalaryIncrement(models.Model):
    employee = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='salary_increments')
    is_percentage = models.BooleanField(default=False, help_text="Check if the increment is a percentage.")
    increment_amount = models.FloatField(help_text="The increment amount or percentage.")
    effective_date = models.DateField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='salary_increment_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validate that effective_date is not in the past
        from django.utils.timezone import now
        if self.effective_date < now().date():
            raise ValidationError("Effective date cannot be in the past.")

    def apply_increment(self, basic_salary):
        """
        Calculate the incremented salary.
        """
        if self.is_percentage:
            incremented_salary = basic_salary + (basic_salary * (self.increment_amount / 100))
        else:
            incremented_salary = basic_salary + self.increment_amount
        return round(incremented_salary, 2)

    def __str__(self):
        increment_type = "Percentage" if self.is_percentage else "Flat Amount"
        return f"Increment for {self.employee.staff_field.name} ({increment_type}) on {self.effective_date}"

class TaxProfile(models.Model):
    class TaxType(models.TextChoices):
        INCOME_TAX = 'Income Tax', 'Income Tax'
        CPF = 'CPF', 'CPF'

    class Gender(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    employee = models.OneToOneField(StaffProfile, on_delete=models.CASCADE, related_name='tax_profile')
    tax_type = models.CharField(max_length=20, choices=TaxType.choices)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    is_senior_citizen = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    is_freedom_fighter = models.BooleanField(default=False)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cpf_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cpf_employee_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cpf_employer_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    salary_process = models.ForeignKey(SalaryProcess, on_delete=models.SET_NULL, null=True, blank=True, related_name='tax_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_annual_income(self):
        """
        Calculate annual income from salary details.
        """
        if self.salary_process:
            monthly_salary = Decimal(str(self.salary_process.total_salary)) or Decimal('0.00')
            self.annual_income = monthly_salary * Decimal('12')  # Assuming 12 months in a year
        else:
            self.annual_income = Decimal('0.00')  # Default to 0 if no salary process linked
        self.save()


    def calculate_tax(self):
        self.calculate_annual_income()  # Ensure annual income is up-to-date
        tax_free_threshold = self.get_tax_free_threshold()
        if self.tax_type == 'Income Tax':
            self.tax_amount = self.get_income_tax(self.annual_income, tax_free_threshold)
        elif self.tax_type == 'CPF':
            self.cpf_employee_contribution, self.cpf_employer_contribution = self.get_cpf_contribution(self.annual_income)
        self.save()

    def get_tax_free_threshold(self):
        if self.is_freedom_fighter:
            return Decimal('475000')
        elif self.is_disabled:
            return Decimal('450000')
        elif self.is_senior_citizen or self.gender == 'Female':
            return Decimal('350000')
        else:
            return Decimal('300000')

    @staticmethod
    def get_income_tax(income, tax_free_threshold):
        taxable_income = max(Decimal('0.00'), income - tax_free_threshold)
        if taxable_income <= 300000:
            return Decimal('0.00')  # No tax
        elif taxable_income <= 600000:
            return taxable_income * Decimal('0.10')  # 10%
        elif taxable_income <= 1200000:
            return taxable_income * Decimal('0.15')  # 15%
        else:
            return taxable_income * Decimal('0.25')  # 25%

    @staticmethod
    def get_cpf_contribution(income):
        employee_contribution = income * Decimal('0.08')  # 8% CPF employee contribution
        employer_contribution = income * Decimal('0.12')  # 12% CPF employer contribution
        return employee_contribution, employer_contribution

    def __str__(self):
        return f"{self.employee.staff_field.name} - {self.tax_type}"


class Notification(models.Model):
    notification_date= models.DateField()
    notification_for=models.ForeignKey(Group,on_delete=models.CASCADE)
    notification=models.TextField(max_length=150)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.notification_date)
    
class Notice(models.Model):
    date=models.DateField()
    notice_title=models.CharField(max_length=150)
    notice_description=models.TextField()
    expire_date=models.DateField()
    file_attached=models.FileField(upload_to="notice",null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='notice_creator')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.notice_title 
    
    
class SMSUsage(models.Model):
    type=( 
        ('MASKING','MASKING'),
        ('NONMASKING','NONMASKING')
    )
    Msg_type = models.CharField(max_length=10, choices=type, default="NONMASKING")
    total_sms = models.IntegerField(default=0)
    expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total SMS Count ({self.Msg_type}): {self.total_sms}"
    
    @property
    def check_expiration_date(self):
        current_datetime = timezone.now()
        if self.expiration_date < current_datetime:
            self.total_sms = 0
            self.save()

class SMSLimit(models.Model):
    type=(
        ('MASKING','MASKING'),
        ('NONMASKING','NONMASKING')
    )
    sms_limit = models.IntegerField(default=0)
    Msg_type = models.CharField(max_length=10, choices=type, default="NONMASKING")
    expiration_date = models.DateTimeField(default=timezone.now)
    unit_price = models.FloatField(null=True, blank=True)
    usage = models.ForeignKey(SMSUsage, on_delete=models.CASCADE,null=True, blank=True, related_name='limits')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total {self.Msg_type} amount is {self.sms_limit}"
    
    def total_price(self): 
        price = self.sms_limit * self.unit_price
        return price
     
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update total_sms in associated SMSUsage instance
        usage = self.usage
        if usage.Msg_type == self.Msg_type:
            usage.total_sms += self.sms_limit
            usage.save()

        usage.expiration_date = max(usage.expiration_date, self.expiration_date)
        usage.save()


class SMSTemplate(models.Model):
    title= models.CharField(max_length=100)
    body= models.CharField(max_length=800)

    def __str__(self): 
        return self.title
    
class SMSTemplateNotification(models.Model):
    type=( 
        ('Attendance Present','Attendance Present'),
        ('Attendance Absent','Attendance Absent'),
        ('Pay Slip Info','Pay Slip Info'), 
        ('Total Due Info','Total Due Info'),
        ('Monthly Due Info','Monthly Due Info'),
        ('Exam Result','Exam Result'),
        ('Salary Payment','Salary Payment'),
    )
    status=(
        ('Active','Active'),
        ('Inactive','Inactive')
    )
    title= models.CharField(max_length=100)
    body= models.CharField(max_length=800)
    notification_type=models.CharField(max_length=20,choices=type)
    notification_status=models.CharField(max_length=20,choices=status,null=True,blank=True)
    def __str__(self): 
        return self.title
    
class SMS(models.Model):
    title= models.CharField(max_length=100, null=True,blank=True)
    mobile=models.CharField(max_length=15)
    msg=models.TextField()
    response=models.TextField(null=True,blank=True)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,related_name='sms_creator')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.mobile
    
    class Meta:
        verbose_name_plural = "SMS"

class Download(models.Model):
    type=( 
        ('Assignment','Assignment'),
        ('Hand Book','Hand Book'),
        ('Home Work','Home Work'),
        ('Class Notes','Class Notes'),
        ('Others Download','Others Download')
    )
    title= models.CharField(max_length=100, null=True,blank=True)
    download_type=models.CharField(max_length=20,choices=type)
    files=models.ImageField(upload_to='download')
    class_id=models.ForeignKey(ClassConfig,on_delete=models.CASCADE)
    academic_year=models.ForeignKey(Admission_Year, on_delete=models.SET_NULL,null=True,blank=True)
    academic_session_year = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class ReportTask(models.Model):
    TASK_TYPES = (
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
    )
    
    task_id = models.CharField(max_length=255, unique=True)
    task_type = models.CharField(max_length=10, choices=TASK_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    file_path = models.CharField(max_length=255, null=True)
    error_message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
