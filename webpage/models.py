from django.db import models
from miscellaneous.models import Institute      
from colorfield.fields import ColorField
from core.models import StuGroup

class Banner(models.Model):
    status=( 
        ('ACTIVE','ACTIVE'), 
        ('INACTIVE','INACTIVE')
    )
    heading =models.CharField(max_length=100,null=True,blank=True)
    banner_image= models.ImageField(upload_to="website", null=True, blank=True)
    status = models.CharField(max_length=10, choices=status,default='ACTIVE')

    def __str__ (self):
            return str(self.heading) 
    

class School_history(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      
      heading =models.CharField(max_length=100,null=True,blank=True)
      text = models.TextField(null=True,blank=True)
      img= models.ImageField(upload_to='website',null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return self.heading
      
class SchoolHistoryImage(models.Model):
    school_history = models.ForeignKey(
        School_history, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='website')

    def __str__(self):
        return f"Image for {self.school_history.heading}"
      
class Msg_from_head(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )

      img= models.ImageField(upload_to='page',null=True,blank=True)
      heading = models.CharField(max_length=100,null=True,blank=True)
      name = models.CharField(max_length=100,null=True,blank=True)
      text = models.TextField(null=True,blank=True)
      whatsapps = models.CharField(max_length=15,null=True,blank=True)
      facebook = models.CharField(max_length=100,null=True,blank=True)
      linkedin = models.CharField(max_length=100,null=True,blank=True)
      twitter = models.CharField(max_length=100,null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return self.heading
      
      
class Msg_from_other(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )

      img= models.ImageField(upload_to='page',null=True,blank=True)
      heading = models.CharField(max_length=100,null=True,blank=True)
      name = models.CharField(max_length=100,null=True,blank=True)
      text = models.TextField(null=True,blank=True)
      whatsapps = models.CharField(max_length=15,null=True,blank=True)
      facebook = models.CharField(max_length=100,null=True,blank=True)
      linkedin = models.CharField(max_length=100,null=True,blank=True)
      twitter = models.CharField(max_length=100,null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return self.heading
    
class ImportantLink(models.Model):
      image = models.ImageField( upload_to="website", null=True, blank=True)
      headline = models.CharField(max_length=100)
      link = models.CharField(max_length=100)

      def __str__ (self):
            return self.headline
    
class Credentials(models.Model):
      headline = models.CharField(max_length=100)
      image = models.ImageField(upload_to="website", null=True, blank=True)
      o_image = models.ImageField(upload_to="website", null=True, blank=True)

      def __str__ (self):
            return self.headline


class Feature(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      icon=models.ImageField(upload_to="website", null=True, blank=True)
      title= models.CharField(max_length=50,null=True,blank=True)
      service_text=models.CharField(max_length= 130,null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return str(self.title)

class Iconic_Student(models.Model):
      name = models.CharField(max_length=100)
      image = models.ImageField(upload_to="website", null=True, blank=True)
      degination = models.CharField(max_length=100)
      batch_year = models.CharField(max_length=4)
      test= models.TextField()

      def __str__ (self):
            return str(self.name)


class Gallery(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      featured=models.BooleanField(default=False)
      title= models.CharField(max_length=20,null=True,blank=True)
      galary_image = models.ImageField(upload_to="website",null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return str(self.title)
      
class Video_Gallery(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      featured=models.BooleanField(default=False)
      heading=models.CharField(max_length=100,null=True,blank=True)
      sub_heading=models.CharField(max_length=100,null=True,blank=True)
      img=models.ImageField(upload_to="website",null=True,blank=True)
      link=models.CharField(max_length=200,null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):     
            return str(self.heading)

class Testimonial(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      name= models.CharField(max_length=50,null=True,blank=True)
      testimonial_image = models.ImageField(upload_to="website",null=True,blank=True)  
      profession =models.CharField(max_length=50, null=True, blank = True)
      text = models.CharField(max_length=150, null=True, blank=True)
      star = models.IntegerField(default=5)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return str(self.name) 
      

  
class Contact(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      text = models.CharField(max_length = 255, null=True, blank = True)
      office_address= models.CharField(max_length= 50, null=True, blank =True)
      mobile = models.CharField(max_length= 15, null=True, blank= True)
      email = models.CharField(max_length= 70, null=True, blank= True)
      google_map= models.TextField(null=True, blank=True)
      image = models.ImageField(null=True, blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return str(self.office_address)

class Public_msg(models.Model):
      name= models.CharField(max_length=100)
      subject= models.CharField(max_length=255,null=True,blank=True)
      email_id = models.CharField(max_length=100,null=True,blank=True)
      phone_no = models.CharField(max_length=15)
      msg = models.TextField()

      def __str__ (self):
            return str(self.name)

      
class Link_name(models.Model):
      name=models.CharField(max_length=100)

      def __str__ (self):
            return str(self.name)
      
class Link(models.Model):
      title = models.CharField(max_length=150)
      link_id=models.ForeignKey(Link_name, models.CASCADE, related_name='page_link')
      link=models.CharField(max_length=130)
      ordered=models.CharField(max_length=50,null=True,blank=True)

      def __str__ (self):
            return str(self.link_id.name)


class Committee(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      name = models.CharField(max_length=100)
      img = models.ImageField(upload_to="website",null=True,blank=True) 
      degination = models.CharField(max_length=100)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return str(self.name)

class Welcome_Speech(models.Model):
      status=( 
        ('ACTIVE','ACTIVE'),
        ('INACTIVE','INACTIVE')
      )
      text = models.CharField(max_length=150, null=True, blank=True)
      description = models.TextField(null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='ACTIVE')

      def __str__ (self):
            return str("Welcome_Speech")


class Site_color(models.Model):
      background_color = ColorField(default='#FF0000')
      menu_color = ColorField(default='#FF0000')
      primary_color = ColorField(default='#FF0000')
      secondary_color = ColorField(default='#FF0000')
      primary_lite_color = ColorField(default='#FF0000')
      text_color = ColorField(default='#FF0000')

      def __str__ (self):
            return str("Site Color")

class Seat_info(models.Model):
      class_id = models.ForeignKey(StuGroup,on_delete=models.CASCADE,related_name="seat_info")
      no_of_seat= models.IntegerField(default=0)

      def __str__ (self):
            return str(self.no_of_seat)
      
class Dress_code(models.Model):
      status=(
        ('Boys','Boys'),
        ('Girls','Girls')
      )
      description = models.TextField(null=True,blank=True)
      dress_image = models.ImageField(upload_to="dress",null=True,blank=True)
      status = models.CharField(max_length=10, choices=status,default='Boys')

      def __str__ (self):
            return str(self.status)



