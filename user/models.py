from django.db import models
from django.contrib.auth.models import Group
from shared.models import CustomUser
from .managers import *
from core.models import ClassConfig,Admission_Year,AcademicSession,StudentShift
from django.db.models.signals import post_save
from django.dispatch import receiver

class Staff(CustomUser):
    class Meta:
        proxy = True

    objects = StaffManager()

    def save(self, *args, **kwargs):
        super(Staff, self).save(*args, **kwargs)
        group, created = Group.objects.get_or_create(name='staff')
        self.groups.set([group])


class Parent(CustomUser): 
    class Meta:
        proxy = True

    objects = ParentManager()

    def save(self, *args, **kwargs):
            super(Parent, self).save(*args, **kwargs)
            group, created = Group.objects.get_or_create(name='parent')
            self.groups.set([group])

class Student(CustomUser):
    class Meta:
        proxy = True

    objects = StudentManager()

    def save(self, *args, **kwargs):
            super(Student, self).save(*args, **kwargs)
            group, created = Group.objects.get_or_create(name='student')
            self.groups.set([group])

class RoleType(models.Model):
     class Status(models.TextChoices):
        ACTIVE = 'Active',
        DEACTIVE = 'Deactive',
     name=models.CharField(max_length=50)
     status=models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)

     def __str__(self):
        return str(self.name)

class Department(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'Active',
        DEACTIVE = 'Deactive',
    name=models.CharField(max_length=50)
    status=models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return str(self.name)
    
class StaffProfile(models.Model):
    
    class Marital_Status(models.TextChoices):
        SINGLE = 'SINGLE', 'SINGLE'
        MARRIED = 'MARRIED', 'MARRIED'
        UNMARRIED = 'UNMARRIED', 'UNMARRIED'
        WIDOWED = 'WIDOWED', 'WIDOWED'
        SEPARATED = 'SEPARATED', 'SEPARATED'
        DIVORCED = 'DIVORCED', 'DIVORCED'

    class Staff_Type(models.TextChoices):
        Permanent = 'Permanent', 'Permanent'
        Temporary = 'Temporary', 'Temporary'
        Contractual = 'Contractual', 'Contractual'

    class Job_Nature(models.TextChoices):
        Fulltime = 'Fulltime', 'Fulltime'
        Parttime = 'Parttime', 'Parttime'

    class Grade(models.TextChoices):
        FirstGrade = 'FirstGrade', 'FirstGrade'
        SecondGrade = 'SecondGrade', 'SecondGrade'
        ThirdGrade = 'ThirdGrade', 'ThirdGrade'
        ForthGrade = 'ForthGrade', 'ForthGrade'
        FifthGrade = 'FifthGrade', 'FifthGrade'
    
    class TVersion(models.TextChoices):
        BANGLA = 'Bangla',
        ENGLISH = 'English',
    
    staff_field = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff_profile')
    short_name =models.CharField(max_length=50,null=True,blank=True)
    name_tag =models.CharField(max_length=50,null=True,blank=True)
    tin =models.CharField(max_length=50,null=True,blank=True)
    qualification=models.CharField(max_length=50,null=True,blank=True)
    fathers_name=models.CharField(max_length=50,null=True,blank=True)
    mothers_name=models.CharField(max_length=50,null=True,blank=True)
    spouse_name=models.CharField(max_length=50,null=True,blank=True)
    spouse_phone_number=models.CharField(max_length=15,null=True,blank=True)
    children_no=models.IntegerField(null=True,blank=True)
    marital_status =models.CharField(max_length=10, choices=Marital_Status.choices, null=True,blank=True)
    staff_id_no=models.CharField(max_length=20)
    employee_type=models.CharField(max_length=30, choices=Staff_Type.choices,null=True,blank=True)
    job_nature=models.CharField(max_length=30, choices=Job_Nature.choices,null=True,blank=True)
    grade=models.CharField(max_length=30, choices=Grade.choices,null=True,blank=True)
    designation=models.CharField(max_length=50,null=True,blank=True)
    joining_date = models.DateField(null=True, blank=True)
    is_staff = models.BooleanField(default=True)
    t_version=models.CharField(max_length=8,choices=TVersion.choices, default=TVersion.BANGLA)
    role=models.ForeignKey(RoleType,on_delete=models.SET_NULL, related_name='staff_role',null=True,blank=True)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_department')
    shift_id=models.ForeignKey(StudentShift,on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_shift')
    subject = models.CharField(max_length=100, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        
        super(StaffProfile, self).save(*args, **kwargs)

        if self.role:
            group_name = self.role.name.lower()
            group, created = Group.objects.get_or_create(name=group_name)
            if self.staff_field:
                self.staff_field.groups.set([group])
                
            else:
                print("staff_field is None; cannot assign group.")

    def __str__(self):
        return str(self.staff_field.name)
    

class StudentProfile(models.Model): 
    class Status(models.TextChoices):
        ONLINE = 'Online',
        OFFLINE = 'Offline',
    class Version(models.TextChoices):
        BANGLA = 'Bangla',
        ENGLISH = 'English',
    
    student_field = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_profile')
    status=models.CharField(max_length=8, choices=Status.choices, default=Status.OFFLINE)
    version=models.CharField(max_length=8,choices=Version.choices, default=Version.BANGLA)
    name_tag=models.CharField(max_length=50,null=True,blank=True)
    admission_year_id=models.ForeignKey(Admission_Year,related_name='assign_student_year',on_delete=models.SET_NULL,null=True,blank=True)
    academic_session_year = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)
    class_id=models.ForeignKey(ClassConfig,on_delete=models.SET_NULL,related_name='student_class',null=True)
    roll_no=models.BigIntegerField(null=True,blank=True)  
    birth_certificate= models.ImageField(null=True,blank=True, upload_to="certificate")
    birth_certificate_no=models.CharField(max_length=50,null=True,blank=True)
    nationality=models.CharField(max_length=50,null=True,blank=True)
    tc_no=models.CharField(max_length=50,null=True,blank=True) 
    admission_date=models.DateField(null=True, blank=True)
    tc_certificate= models.ImageField(null=True,blank=True, upload_to="certificate")
    parent_id=models.ForeignKey(Parent,on_delete=models.SET_NULL,blank=True,null=True, related_name="std_parent")
    village= models.CharField(max_length=50,null=True,blank=True)
    post_office= models.CharField(max_length=50,null=True,blank=True)
    ps_or_upazilla= models.CharField(max_length=50,null=True,blank=True)
    district=models.CharField(max_length=50,null=True,blank=True)
    is_migrated=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True) 

    def __str__(self): 
        return str(self.student_field.name) + " " + self.version + " " + self.class_id.class_group_id.class_id.name
    
class  ParentProfile(models.Model):
    parent_field = models.OneToOneField(Parent, on_delete=models.CASCADE, related_name='parent_profile') 
    father_name = models.CharField(max_length= 50,null=True,blank=True)
    father_name_bangla = models.CharField(max_length= 50,null=True,blank=True)
    father_mobile_no = models.CharField(max_length= 15,null=True,blank=True)
    mother_name = models.CharField(max_length= 50,null=True,blank=True)
    mother_name_bangla = models.CharField(max_length= 50,null=True,blank=True)
    mother_mobile_no= models.CharField(max_length= 15,null=True,blank=True)
    relation=models.CharField(max_length= 50,null=True,blank=True)
    f_occupation=models.CharField(max_length=50, null=True,blank=True)
    m_occupation=models.CharField(max_length=50, null=True,blank=True)
    occupation=models.CharField(max_length=50, null=True,blank=True)
    f_nid= models.CharField(max_length=50, null=True,blank=True)
    m_nid= models.CharField(max_length=50, null=True,blank=True)
    g_name = models.CharField(max_length= 50,null=True,blank=True)
    g_mobile_no = models.CharField(max_length= 15,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True) 

    def __str__(self):
        return str(self.parent_field.name) 
    
class ImportedUser(models.Model):
    user_id=models.BigIntegerField(null=True,blank=True,unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    
    
    
    
    
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from shared.models import CustomUser
from .managers import *
from core.models import ClassConfig, Admission_Year, AcademicSession, StudentShift

class AdmissionApplicant(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        APPROVED = 'Approved', 'Approved'
        REJECTED = 'Rejected', 'Rejected'
        PAYMENT_PENDING = 'Payment Pending', 'Payment Pending'
    
    class Shift(models.TextChoices):
        MORNING = 'Morning', 'Morning'
        DAY = 'Day', 'Day'
    
    class Version(models.TextChoices):
        BANGLA = 'Bangla', 'Bangla'
        ENGLISH = 'English', 'English'
    
    class Quota(models.TextChoices):
        NA = 'N/A', 'N/A'
        FQ = 'FQ', 'FQ'  
        EQ = 'EQ', 'EQ' 
    
    # Basic Information
    applicant_id = models.CharField(max_length=20, unique=True, blank=True)
    password = models.CharField(max_length=100)
    class_sought = models.CharField(max_length=100)
    shift = models.CharField(max_length=10, choices=Shift.choices, default=Shift.DAY)
    version = models.CharField(max_length=10, choices=Version.choices, default=Version.BANGLA)
    photo = models.ImageField(upload_to='admission_photos/', null=True, blank=True)
    
    # Payment Information
    payment_status = models.CharField(max_length=50, default='Pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_transaction = models.ForeignKey('ssl_commerz.PaymentTransaction', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Applicant Information
    full_name = models.CharField(max_length=150)
    full_name_bangla = models.CharField(max_length=150)
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    birth_certificate_no = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=CustomUser.Gender.choices)
    religion = models.CharField(max_length=14, choices=CustomUser.Religion.choices)
    dob = models.DateField()
    blood_group = models.CharField(max_length=4, choices=CustomUser.Blood_Group.choices, blank=True, null=True)
    nationality = models.CharField(max_length=50)
    catchment_area = models.BooleanField(default=False)
    quota = models.CharField(max_length=10, choices=Quota.choices, default=Quota.NA)
    
    # Academic Information
    previous_class = models.CharField(max_length=100, blank=True, null=True)
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    previous_school_address = models.TextField(blank=True, null=True)
    exam_name = models.CharField(max_length=50, blank=True, null=True)
    board_roll = models.CharField(max_length=50, blank=True, null=True)
    board_name = models.CharField(max_length=100, blank=True, null=True)
    registration_no = models.CharField(max_length=50, blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    # Father Information
    father_name = models.CharField(max_length=150)
    father_name_bangla = models.CharField(max_length=150, blank=True, null=True)
    father_mobile = models.CharField(max_length=15)
    father_qualification = models.CharField(max_length=100, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_service_type = models.CharField(max_length=100, blank=True, null=True)
    father_designation = models.CharField(max_length=100, blank=True, null=True)
    father_organization = models.CharField(max_length=200, blank=True, null=True)
    father_yearly_income = models.CharField(max_length=100, blank=True, null=True)
    father_income_source = models.CharField(max_length=200, blank=True, null=True)
    father_nid = models.CharField(max_length=50, blank=True, null=True)
    father_etin = models.CharField(max_length=50, blank=True, null=True)
    
    # Mother Information
    mother_name = models.CharField(max_length=150)
    mother_name_bangla = models.CharField(max_length=150, blank=True, null=True)
    mother_mobile = models.CharField(max_length=15)
    mother_qualification = models.CharField(max_length=100, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_service_type = models.CharField(max_length=100, blank=True, null=True)
    mother_designation = models.CharField(max_length=100, blank=True, null=True)
    mother_organization = models.CharField(max_length=200, blank=True, null=True)
    mother_yearly_income = models.CharField(max_length=100, blank=True, null=True)
    mother_income_source = models.CharField(max_length=200, blank=True, null=True)
    mother_nid = models.CharField(max_length=50, blank=True, null=True)
    mother_etin = models.CharField(max_length=50, blank=True, null=True)
    
    # Guardian Information (if applicable)
    guardian_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_mobile = models.CharField(max_length=15, blank=True, null=True)
    guardian_relation = models.CharField(max_length=100, blank=True, null=True)
    guardian_nid = models.CharField(max_length=50, blank=True, null=True)
    guardian_address = models.TextField(blank=True, null=True)
    
    # Address Information
    present_address = models.TextField()
    present_country = models.CharField(max_length=50)
    present_district = models.CharField(max_length=50)
    present_thana = models.CharField(max_length=50)
    present_telephone = models.CharField(max_length=20, blank=True, null=True)
    present_mobile = models.CharField(max_length=15, blank=True, null=True)
    
    permanent_address = models.TextField()
    permanent_country = models.CharField(max_length=50)
    permanent_district = models.CharField(max_length=50)
    permanent_thana = models.CharField(max_length=50)
    permanent_telephone = models.CharField(max_length=20, blank=True, null=True)
    permanent_mobile = models.CharField(max_length=15, blank=True, null=True)
    
    # Contact Information
    contact_mobile = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15)
    
    # Status and Dates
    status = models.CharField(max_length=60, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.applicant_id})"
    
    def save(self, *args, **kwargs):
        if not self.applicant_id:
            # Generate a unique applicant ID
            self.applicant_id = self.generate_applicant_id()
            # Set password as phone number if available, otherwise random string
            self.password = make_password(self.contact_mobile or get_random_string(10))
        
        if not self.payment_amount:
            self.payment_amount = self.get_admission_fee()
            
        super().save(*args, **kwargs)
        
    def get_admission_fee(self):
        # Define your admission fee structure here
        fee_structure = {
            'Six': 1000.00,
            'Eight': 1500.00,
            'Nine': 2000.00,
            
        }
        return fee_structure.get(self.class_sought, 1000.00)
    
    def is_payment_completed(self):
        return self.payment_status == 'Completed' and self.payment_transaction and self.payment_transaction.status == 'SUCCESS'
    
    def generate_applicant_id(self):
        # Generate a unique 8-digit applicant ID
        while True:
            applicant_id = f"A{get_random_string(7, '0123456789')}"
            if not AdmissionApplicant.objects.filter(applicant_id=applicant_id).exists():
                return applicant_id
    
    def migrate_to_student(self):
        # Create CustomUser (Student) from admission data
        student = Student(
            username=self.applicant_id,
            phone_number=self.contact_mobile,
            name=self.full_name,
            name_in_bangla=self.full_name_bangla,
            avatar=self.photo,
            gender=self.gender,
            religion=self.religion,
            dob=self.dob,
            blood_group=self.blood_group,
            nid=self.birth_certificate_no,
            present_address=self.present_address,
            permanent_address=self.permanent_address,
            user_id=int(self.applicant_id[1:]),  # Remove 'A' prefix
            password=self.password
        )
        student.save()
        
        # Create Parent record if guardian info exists
        parent = None
        if self.guardian_name:
            parent = Parent(
                username=self.guardian_mobile or f"P{self.applicant_id[1:]}",
                phone_number=self.guardian_mobile,
                name=self.guardian_name,
                nid=self.guardian_nid,
                password=make_password(self.guardian_mobile or get_random_string(10)))
            parent.save()
        
        # Create StudentProfile
        student_profile = StudentProfile(
            student_field=student,
            version=self.version,
            name_tag=self.nick_name,
            birth_certificate_no=self.birth_certificate_no,
            nationality=self.nationality,
            parent_id=parent,
            village=self.permanent_address.split(',')[0] if self.permanent_address else '',
            district=self.permanent_district,
            ps_or_upazilla=self.permanent_thana
        )
        student_profile.save()
        
        # Create ParentProfile if parent exists
        if parent:
            parent_profile = ParentProfile(
                parent_field=parent,
                father_name=self.father_name,
                father_name_bangla=self.father_name_bangla,
                father_mobile_no=self.father_mobile,
                mother_name=self.mother_name,
                mother_name_bangla=self.mother_name_bangla,
                mother_mobile_no=self.mother_mobile,
                f_occupation=self.father_occupation,
                m_occupation=self.mother_occupation,
                f_nid=self.father_nid,
                m_nid=self.mother_nid
            )
            parent_profile.save()
        
        return student
    
    


#class xi here.......................################
class AdmissionForm(models.Model):
    # Basic Information
    class_sought = models.CharField(max_length=50, default='Class XI')
    # shift = models.CharField(max_length=20, choices=[('Morning', 'Morning'), ('Day', 'Day')])
    # version = models.CharField(max_length=20, choices=[('Bangla', 'Bangla'), ('English', 'English')])
    
    board_application_id = models.CharField(max_length=50, verbose_name="Board Application ID", blank=True, null=True)
    ex_rajuk_student = models.BooleanField(default=False, verbose_name="Ex-Rajuk Student")
    
    # Applicant Information
    fullName = models.CharField(max_length=100, verbose_name="Applicant's Name [English]")
    nickName = models.CharField(max_length=50, verbose_name="Nick Name")
    brcn = models.CharField(max_length=50, verbose_name="Birth Register Certificate Number")
    gender = models.CharField(max_length=10, choices=[('Female', 'Female'), ('Male', 'Male')])
    religion = models.CharField(max_length=20, choices=[
        ('Islam', 'Islam'), 
        ('Hindu', 'Hindu'),
        ('Christian', 'Christian'),
        ('Buddha', 'Buddha')
    ])
    fullNameBangla = models.CharField(max_length=100, verbose_name="Applicant's Name [বাংলা]")
    birthDate = models.DateField(verbose_name="Date of Birth")
    bloodGroup = models.CharField(max_length=5, blank=True, null=True, choices=[
        ('A+', 'A+'), ('A-', 'A-'), 
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-')
    ])
    nationality = models.CharField(max_length=50)
    catchmentArea = models.BooleanField(default=False, verbose_name="Catchment Area")
    quota = models.CharField(max_length=10, choices=[
        ('N/A', 'N/A'), 
        ('FQ', 'FQ'), 
        ('EQ', 'EQ')
    ], default='N/A')
    
    # Academic Information
    previous_class = models.CharField(max_length=50, verbose_name="Previous Class")
    boardRoll = models.CharField(max_length=50, verbose_name="Board Roll")
    boardName = models.CharField(max_length=100, verbose_name="Board Name")
    exam = models.CharField(max_length=20, default='SSC')
    registrationNo = models.CharField(max_length=50, verbose_name="Reg No.")
    gpa = models.CharField(max_length=10, verbose_name="GPA")
    
    # Parent Information
    fatherName = models.CharField(max_length=100, verbose_name="Father's Name")
    fatherMobile = models.CharField(max_length=15, verbose_name="Father's Mobile")
    fatherOccupation = models.CharField(max_length=100, verbose_name="Father's Occupation")
    
    motherName = models.CharField(max_length=100, verbose_name="Mother's Name")
    motherMobile = models.CharField(max_length=15, verbose_name="Mother's Mobile")
    motherOccupation = models.CharField(max_length=100, verbose_name="Mother's Occupation")
    
    # Contact Information
    smsAlertNumber = models.CharField(max_length=15, verbose_name="Mobile Number For Contact/SMS")
    
    # Address
    praddress = models.TextField(verbose_name="Present Address")
    prCountry = models.CharField(max_length=50, verbose_name="Present Country")
    prDistrict = models.CharField(max_length=50, verbose_name="Present District")
    prThana = models.CharField(max_length=50, verbose_name="Present Thana/Upazilla")
    prTelephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Present Telephone")
    prMobile = models.CharField(max_length=15, verbose_name="Present Mobile")
    
    paddress = models.TextField(verbose_name="Permanent Address")
    pCountry = models.CharField(max_length=50, verbose_name="Permanent Country")
    pDistrict = models.CharField(max_length=50, verbose_name="Permanent District")
    pThana = models.CharField(max_length=50, verbose_name="Permanent Thana/Upazilla")
    pTelephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Permanent Telephone")
    pMobile = models.CharField(max_length=15, verbose_name="Permanent Mobile")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullName} - {self.class_sought}"
    
    
    
from django.db import models

# List of all Bangladesh districts
DISTRICT_CHOICES = [
    ('Bagerhat', 'Bagerhat'),
    ('Bandarban', 'Bandarban'),
    ('Barguna', 'Barguna'),
    ('Barishal', 'Barishal'),
    ('Bhola', 'Bhola'),
    ('Bogra', 'Bogra'),
    ('Brahmanbaria', 'Brahmanbaria'),
    ('Chandpur', 'Chandpur'),
    ('Chapainawabganj', 'Chapainawabganj'),
    ('Chattogram', 'Chattogram'),
    ('Chuadanga', 'Chuadanga'),
    ('Cumilla', 'Cumilla'),
    ('Cox\'s Bazar', 'Cox\'s Bazar'),
    ('Dhaka', 'Dhaka'),
    ('Dinajpur', 'Dinajpur'),
    ('Faridpur', 'Faridpur'),
    ('Feni', 'Feni'),
    ('Gaibandha', 'Gaibandha'),
    ('Gazipur', 'Gazipur'),
    ('Gopalganj', 'Gopalganj'),
    ('Habiganj', 'Habiganj'),
    ('Jamalpur', 'Jamalpur'),
    ('Jashore', 'Jashore'),
    ('Jhalokati', 'Jhalokati'),
    ('Jhenaidah', 'Jhenaidah'),
    ('Joypurhat', 'Joypurhat'),
    ('Khagrachhari', 'Khagrachhari'),
    ('Khulna', 'Khulna'),
    ('Kishoreganj', 'Kishoreganj'),
    ('Kurigram', 'Kurigram'),
    ('Kushtia', 'Kushtia'),
    ('Lakshmipur', 'Lakshmipur'),
    ('Lalmonirhat', 'Lalmonirhat'),
    ('Madaripur', 'Madaripur'),
    ('Magura', 'Magura'),
    ('Manikganj', 'Manikganj'),
    ('Meherpur', 'Meherpur'),
    ('Moulvibazar', 'Moulvibazar'),
    ('Munshiganj', 'Munshiganj'),
    ('Mymensingh', 'Mymensingh'),
    ('Naogaon', 'Naogaon'),
    ('Narail', 'Narail'),
    ('Narayanganj', 'Narayanganj'),
    ('Narsingdi', 'Narsingdi'),
    ('Natore', 'Natore'),
    ('Netrokona', 'Netrokona'),
    ('Nilphamari', 'Nilphamari'),
    ('Noakhali', 'Noakhali'),
    ('Pabna', 'Pabna'),
    ('Panchagarh', 'Panchagarh'),
    ('Patuakhali', 'Patuakhali'),
    ('Pirojpur', 'Pirojpur'),
    ('Rajbari', 'Rajbari'),
    ('Rajshahi', 'Rajshahi'),
    ('Rangamati', 'Rangamati'),
    ('Rangpur', 'Rangpur'),
    ('Satkhira', 'Satkhira'),
    ('Shariatpur', 'Shariatpur'),
    ('Sherpur', 'Sherpur'),
    ('Sirajganj', 'Sirajganj'),
    ('Sunamganj', 'Sunamganj'),
    ('Sylhet', 'Sylhet'),
    ('Tangail', 'Tangail'),
    ('Thakurgaon', 'Thakurgaon'),
]

CLASS_CHOICES = [
    ('Class VI', 'Class VI'),
    ('Class VII', 'Class VII'),
    ('Class VIII', 'Class VIII'),
    ('Class IX', 'Class IX'),
    ('Class X', 'Class X'),
    ('Class XI', 'Class XI'),
    ('Class XII', 'Class XII'),
    ('SSC', 'SSC'),
    ('HSC', 'HSC'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

MARITAL_STATUS_CHOICES = [
    ('Married', 'Married'),
    ('Unmarried', 'Unmarried'),
]

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

class Registration(models.Model):
    registration_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    occupation = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    email = models.EmailField()
    admitted_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    passing_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    admit_year = models.PositiveIntegerField()
    passing_year = models.PositiveIntegerField()
    nid = models.CharField(max_length=20)
    picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    present_address = models.TextField()
    present_district = models.CharField(max_length=50, choices=DISTRICT_CHOICES)
    permanent_address = models.TextField()
    permanent_district = models.CharField(max_length=50, choices=DISTRICT_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=250.00)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registration_id} - {self.full_name}"
    
    
class SpinEntry(models.Model):
    spin_name = models.CharField(max_length=100)
    spin_phone = models.CharField(max_length=20, unique=True)
    spin_institute = models.CharField(max_length=200)
    spin_num_students = models.IntegerField()
    spin_result = models.IntegerField(null=True, blank=True)
    spin_has_spun = models.BooleanField(default=False)