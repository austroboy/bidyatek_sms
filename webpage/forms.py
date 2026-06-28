from django.forms import ModelForm
from .models import *


class BannerForm(ModelForm):
    class Meta:
        model=Banner
        fields= '__all__'

class GalleryForm(ModelForm):
    class Meta:
        model=Gallery
        fields= '__all__'

class VGalleryForm(ModelForm):
    class Meta:
        model=Video_Gallery
        fields= '__all__'

class TestimonialForm(ModelForm):
    class Meta:
        model=Testimonial
        fields= '__all__'

class ContactFrom(ModelForm):
    class Meta:
        model=Contact
        fields= '__all__'

