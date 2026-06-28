from django.contrib import admin
from .models import *

# Register your models here.
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_field', 'version', 'class_id', 'roll_no', 'status', 'admission_year_id')  # Fields to display in list view
    list_filter = ('class_id', 'version', 'status', 'admission_year_id')  # Fields to filter by

    search_fields = ('student_field__name', 'class_id__class_group_id__class_id__name', 'roll_no')  # Add search functionality

admin.site.register(StudentProfile, StudentProfileAdmin)

admin.site.register(ParentProfile)
admin.site.register(Parent)
admin.site.register(StaffProfile)
admin.site.register(RoleType)

admin.site.register(ImportedUser)
class StudentModelAdmin(admin.ModelAdmin):
    list_per_page = 1000

admin.site.register(Student, StudentModelAdmin)



@admin.register(AdmissionApplicant)
class AdmissionApplicantAdmin(admin.ModelAdmin):
    list_display = (
        'applicant_id', 'full_name', 'class_sought', 'shift', 'version',
        'status', 'contact_mobile', 'applied_at'
    )
    list_filter = ('shift', 'version', 'status', 'class_sought', 'quota', 'applied_at')
    search_fields = ('applicant_id', 'full_name', 'contact_mobile', 'father_mobile', 'mother_mobile', 'guardian_mobile')
    readonly_fields = ('applicant_id', 'applied_at', 'updated_at')
    date_hierarchy = 'applied_at'
    ordering = ('-applied_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('applicant_id', 'password', 'class_sought', 'shift', 'version', 'photo')
        }),
        ('Applicant Information', {
            'fields': ('full_name', 'full_name_bangla', 'nick_name', 'birth_certificate_no', 'gender', 'religion', 'dob', 'blood_group', 'nationality', 'catchment_area', 'quota')
        }),
        ('Academic Information', {
            'fields': ('previous_class', 'previous_school', 'previous_school_address', 'exam_name', 'board_roll', 'board_name', 'registration_no', 'gpa')
        }),
        ('Father Information', {
            'fields': ('father_name', 'father_name_bangla', 'father_mobile', 'father_qualification', 'father_occupation', 'father_service_type', 'father_designation', 'father_organization', 'father_yearly_income', 'father_income_source', 'father_nid', 'father_etin')
        }),
        ('Mother Information', {
            'fields': ('mother_name', 'mother_name_bangla', 'mother_mobile', 'mother_qualification', 'mother_occupation', 'mother_service_type', 'mother_designation', 'mother_organization', 'mother_yearly_income', 'mother_income_source', 'mother_nid', 'mother_etin')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_mobile', 'guardian_relation', 'guardian_nid', 'guardian_address')
        }),
        ('Address Information', {
            'fields': ('present_address', 'present_country', 'present_district', 'present_thana', 'present_telephone', 'present_mobile',
                       'permanent_address', 'permanent_country', 'permanent_district', 'permanent_thana', 'permanent_telephone', 'permanent_mobile')
        }),
        ('Contact Information', {
            'fields': ('contact_mobile', 'emergency_contact')
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'applied_at', 'updated_at')
        }),
    )
    
    
@admin.register(SpinEntry)
class SpinEntryAdmin(admin.ModelAdmin):
    list_display = ('spin_name', 'spin_phone', 'spin_institute', 'spin_num_students', 'spin_has_spun', 'spin_result')
    list_filter = ('spin_has_spun', 'spin_institute')
    search_fields = ('spin_name', 'spin_phone', 'spin_institute')
    readonly_fields = ('spin_result',)
    list_editable = ('spin_has_spun',)
    ordering = ('spin_name',)