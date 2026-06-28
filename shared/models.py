from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):

    class Gender(models.TextChoices):
        MALE = 'Male',
        FEMALE = 'Female',
        OTHER = 'Other',
    
    class Status(models.TextChoices):
        ACTIVE = 'Active',
        DEACTIVE = 'Deactive',
    
    class Religion(models.TextChoices):
        Islam = 'Islam', 
        Christianity = 'Christianity',
        Hinduism = 'Hinduism',
        Buddhism = 'Buddhism',
        OTHER = 'Other',
    
    class Blood_Group(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

  
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    last_name = None
    first_name = None
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    name_in_bangla = models.CharField(max_length=150, null=True, blank=True)
    avatar=models.ImageField(upload_to='profile_pic',null=True,blank=True)
    gender = models.CharField(max_length=6, choices=Gender.choices, default=Gender.MALE, null=True, blank=True)
    religion=models.CharField(max_length=14,choices=Religion.choices,null=True,blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group=models.CharField(max_length=4,choices=Blood_Group.choices,null=True,blank=True)
    email = models.EmailField(verbose_name='Email Address', null=True,blank=True)
    nid=models.CharField(max_length=50, null=True, blank=True)
    rfid=models.CharField(max_length=20,unique=True,null=True,blank=True)
    user_id=models.BigIntegerField(null=True,blank=True,unique=True)
    barcode=models.ImageField(blank=True,null=True,upload_to='barcode')
    present_address=models.TextField(null=True,blank=True)
    permanent_address=models.TextField(null=True,blank=True)
    disability_info=models.CharField(max_length=50,null=True,blank=True)
    status=models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,related_name='+')
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,related_name='+')

    def __str__(self):
        return self.name if self.name else self.username
    

class User_wallet(models.Model):
    user_id=models.ForeignKey(CustomUser, models.CASCADE, related_name="user_wallet")
    wallet= models.FloatField(null=True,blank=True)

    def __str__(self):
        return self.user_id.name + " " + self.wallet

