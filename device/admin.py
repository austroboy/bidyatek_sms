from django.contrib import admin
from .models import BiometricDevice, DevicePunchLog


@admin.register(BiometricDevice)
class BiometricDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'port', 'is_exit_device',
                    'is_active', 'last_sync')
    list_filter = ('is_active', 'is_exit_device', 'device_type')
    search_fields = ('name', 'ip_address')


@admin.register(DevicePunchLog)
class DevicePunchLogAdmin(admin.ModelAdmin):
    list_display = ('device_user_id', 'punch_time', 'person_type',
                    'source', 'processed', 'sms_sent', 'device')
    list_filter = ('person_type', 'source', 'processed', 'sms_sent')
    search_fields = ('device_user_id', 'matched_user_id', 'note')
    date_hierarchy = 'punch_time'
    readonly_fields = ('created_at',)
