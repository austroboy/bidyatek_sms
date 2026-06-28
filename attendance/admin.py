from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Holiday)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'attendance_date', 'academic_year', 'created_at', 'updated_at')
admin.site.register(StudentAttendance, StudentAttendanceAdmin)
admin.site.register(StudentAttendanceLog)
admin.site.register(StaffAttendance)
admin.site.register(StaffAttendanceLog)
admin.site.register(HostelAttendance)
admin.site.register(HostelAttendanceLog)
admin.site.register(LeaveType)
admin.site.register(LeaveRequest)
admin.site.register(LeaveQuota)