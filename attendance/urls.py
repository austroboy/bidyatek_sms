from django.urls import path
from .views import *
from .api_view import *

urlpatterns = [

    # api paths 
    path('attendance/<int:student_id>/<int:year>/<int:month>/', StudentMonthlyAttendanceView.as_view(), name='student_monthly_attendance'),
    path('staff-attendance/<int:staff_id>/<int:year>/<int:month>/', StaffMonthlyAttendanceView.as_view(), name='staff_monthly_attendance'),
    path('staff-attendance/logs/<int:staff_id>/', StaffAttendanceLogView.as_view(), name='staff_attendance_logs'),
    path('staff-attendance/create/', StaffAttendanceCreateView.as_view(), name='staff_attendance_create'),
    path('staff-attendance/update/<int:attendance_id>/', StaffAttendanceUpdateView.as_view(), name='staff_attendance_update'),
    path('staff-attendance/report/<int:year>/<int:month>/', StaffAttendanceReportView.as_view(), name='staff_attendance_report'),
    path('leave-request/add/', AddLeaveRequestView.as_view(), name='add_leave_request'),
    path('leave-request/edit/<int:pk>/', EditLeaveRequestView.as_view(), name='edit_leave_request'),
    path('leave-request/delete/<int:pk>/', DeleteLeaveRequestView.as_view(), name='delete_leave_request'),

    # exam    path
    path('attendance/student_attendance/',studentAttendance,name='student_attendance' ),
    path('attendance/student_hostel_attendance/',studentHostelAttendance,name='student_hostel_attendance' ),
    path('student_attendance_save/',saveStudentAttendance,name='student_attendance_save' ),
    path('student_hostel_attendance_save/',saveHostelStudentAttendance,name='student_hostel_attendance_save' ),
    path('get_student_attendance/',get_student_attendance,name='getstudentattendance' ),
    path('get_hostel_student_attendance/',get_hostel_student_attendance,name='get_hostel_student_attendance' ),
    path('attendance_report/stu_report/report_student_attendance/',report_student_attendance,name='report_student_attendance' ),
    path('attendance_report/stu_report/report_date_range_student_attendance/',report_date_student_attendance,name='report_date_student_attendance' ),
    path('attendance_report/stu_report/report_time_student_attendance/',report_time_student_attendance,name='report_time_student_attendance' ),
    
    
    path('attendance/staff_attendance/',staffAttendance,name='staff_attendance' ),
    path('staff_attendance_save/',saveStaffAttendance,name='staff_attendance_save' ),
    path('get_staff_attendance/',get_staff_attendance,name='getstaffattendance' ),
    path('attendance_report/staff_report/report_staff_attendance/',report_staff_attendance,name='report_staff_attendance' ),
    path('attendance_report/staff_report/report_time_staff_attendance/',report_time_staff_attendance,name='report_time_staff_attendance' ),


    path('attendance/leave_quota/',leave_quota,name='leave_quota'),
    path('list_leave_quota/',list_leave_quota,name='list_leave_quota'),
    path('add_leave_quota/',add_leave_quota,name='add_leave_quota'),
    path('leave_quota<int:pk>/edit',edit_leave_quota,name='edit_leave_quota'),
    path('leave_quota<int:pk>/del',del_leave_quota,name='del_leave_quota'),

    path('attendance/leave_type/',leave_type,name='leave_type'),
    path('list_leave_type/',list_leave_type,name='list_leave_type'),
    path('add_leave_type/',add_leave_type,name='add_leave_type'),
    path('leave_type<int:pk>/edit',edit_leave_type,name='edit_leave_type'),
    path('leave_type<int:pk>/del',del_leave_type,name='del_leave_type'),

 
    path('attendance/leave_request/',leave_request,name='leave_request'),
    path('list_leave_request/',list_leave_request,name='list_leave_request'),
    path('attendance/leave_request/add_leave_request/',add_leave_request,name='add_leave_request'),
    path('leave_request<int:pk>/edit',edit_leave_request,name='edit_leave_request'),
    path('leave_request<int:pk>/del',del_leave_request,name='del_leave_request'), 
    path('change_leave_status/', change_leave_status, name='change_leave_status'),


    path('attendance/holiday/',holiday,name='holiday'),
    path('add_holiday/',add_holiday,name='add_holiday'),
    path('attendance<int:pk>/edit',edit_holiday,name='edit_holiday'),
    path('attendance<int:pk>/del',del_holiday,name='del_holiday'),
    path('list_holiday/',list_holiday,name='list_holiday'),
    
]