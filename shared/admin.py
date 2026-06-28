from django.contrib import admin
from .models import *

class CustomUserModelAdmin(admin.ModelAdmin):
    list_per_page = 1000

admin.site.register(CustomUser, CustomUserModelAdmin)