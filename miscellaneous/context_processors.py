from .models import Institute
from django.utils import timezone
from crucial.models import SMSUsage,Notice
from attendance.models import LeaveRequest
from django.db import connection

def institute_context(request):
    if "miscellaneous_institute" not in connection.introspection.table_names():
        return {'institute': None}

    try:
        institute = Institute.objects.latest('id')
    except Institute.DoesNotExist:
        institute = None
    
    return {'institute': institute}

def sms_expiration_check(request):
    sms_usage_expired = []
    
    # Check if the table exists
    if "crucial_smsusage" in connection.introspection.table_names():
        for sms_usage in SMSUsage.objects.all():
            sms_usage.check_expiration_date  # Ensure this line triggers the intended action
    else:
        # Log or handle missing table
        pass
    
    return {'sms_usage_expired': sms_usage_expired}

def leave_request_check(request):
    if "attendance_leaverequest" in connection.introspection.table_names():
        pending_exists = LeaveRequest.objects.filter(status='Pending').exists()
    else:
        pending_exists = None
    return {'leave_request_check': pending_exists}

def notice_list_view(request):
    today = timezone.now().date()
    notice_list_view = Notice.objects.filter(expire_date__gte=today)
    return {'notice_list_view': notice_list_view}