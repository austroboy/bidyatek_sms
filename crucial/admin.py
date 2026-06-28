from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(TeacherSubjectAssign)
admin.site.register(Routine)
admin.site.register(Homework)
admin.site.register(HomeworkSubmission)
admin.site.register(Notice)
admin.site.register(Notification)
admin.site.register(Feetype)
admin.site.register(Fee_package)
admin.site.register(Fee_month)
admin.site.register(Fees_name)
admin.site.register(FeeSubHead)
admin.site.register(PartialPayment)

admin.site.register(MainBalance)
admin.site.register(BalanceStatement)
admin.site.register(ExpenseHead)
admin.site.register(Expenseitemlist)
admin.site.register(IncomeHead)
admin.site.register(IncomeitemList)
admin.site.register(Withdraw)
admin.site.register(SalaryConfiguration) 
admin.site.register(Addition_type)
admin.site.register(Addition)
admin.site.register(Deduction_type)
admin.site.register(Deduction)
admin.site.register(SalaryProcess)
admin.site.register(SMSLimit)
admin.site.register(SMSTemplate)
admin.site.register(SMSTemplateNotification)
admin.site.register(Download)
admin.site.register(Waiver)
admin.site.register(SMS)
admin.site.register(SMSUsage)
admin.site.register(Hostel_package)
admin.site.register(Hostel)
admin.site.register(Tution_package)
admin.site.register(Tution)
admin.site.register(Transport_package)
admin.site.register(Transport)

class FeesAdmin(admin.ModelAdmin):
    list_display = (
        'student_id', 'feetype_id', 'transaction_no', 'amount', 'discount_amount', 
        'created_at', 'updated_at'
    )
    search_fields = (
        'student_id__student_field__user_id', 'transaction_no', 'amount', 'feetype_id__fees_type__feetype',
    )
    list_filter = ('status', 'payment_method')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fields = ['student_id', 'feetype_id', 'amount', 'discount_amount', 'status']

admin.site.register(Fees, FeesAdmin)



from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render
from crucial.models import Fees_name, Fees  

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update-feetype/', self.admin_view(update_feetype), name='update_feetype'),
        ]
        return custom_urls + urls

admin_site = CustomAdminSite(name="custom_admin")  # Use a separate admin instance

def update_feetype(request):
    if not request.user.is_staff:  # Restrict to staff users
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('admin:index')

    if request.method == 'POST':
        old_title = "March - March - Tuition Fee - XII"
        new_title = "June - Test Fee - XII"

        try:
            old_feetype = Fees_name.objects.get(fees_title=old_title)
            new_feetype = Fees_name.objects.get(fees_title=new_title)

            updated_count = Fees.objects.filter(feetype_id=old_feetype).update(feetype_id=new_feetype)
            messages.success(request, f"Successfully updated {updated_count} fees!")

        except Fees_name.DoesNotExist:
            messages.error(request, "One of the fee types could not be found.")

        return redirect('update_feetype')

    return render(request, 'fees/update_feetype.html')

# Register models with the new admin site
admin_site.register(Fees_name)
admin_site.register(Fees)

from .models import ReportTask


@admin.register(ReportTask)
class ReportTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'task_type', 'status', 'file_path', 'created_at')
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('task_id', 'file_path', 'error_message')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('task_id', 'task_type', 'status', 'file_path', 'error_message', 'created_at')
        }),
    )
    
    
@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)