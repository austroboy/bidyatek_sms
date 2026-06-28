from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q,Count, Case, When, IntegerField, F,Value,Subquery
from user.models import StudentProfile,StaffProfile,Student,Staff
from .models import *
from miscellaneous.models import WeekendDay
from core.models import ClassConfig,AcademicSession,ClassGroupConfig
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import date,timedelta
from .forms import *
from django.contrib import messages
import json
from datetime import datetime
from itertools import groupby,chain
from operator import itemgetter
from django.db.models import Q
from user.decorators import *
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.db.models import Sum, F
from django.db.models import ExpressionWrapper, DurationField
from decimal import Decimal


# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user,"teacher", roles=['Manager','HR']))
@csrf_exempt
def saveStudentAttendance(request): 
    id = request.POST.get('id')
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    status = request.POST.get('value')
    student = StudentProfile.objects.get(id=id)
    attendance_date = date.today()
    updated_values = {'status': status, 'academic_year':admission_year}
    obj, created = StudentAttendance.objects.update_or_create(
        name=student, attendance_date=attendance_date,defaults=updated_values
    )
    return JsonResponse({'msg':'success'})


# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user,"teacher", roles=['Manager','HR']))
@csrf_exempt
def saveHostelStudentAttendance(request): 
    id = request.POST.get('id')
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    status = request.POST.get('value')

    try:
        # Get the student instance
        student = StudentProfile.objects.get(id=id)
        # Get the related Hostel instance
        hostel_instance = Hostel.objects.filter(student_id=student, academic_year=admission_year).first()

        if not hostel_instance:
            return JsonResponse({'msg': 'Hostel record not found for the student'}, status=400)

        attendance_date = date.today()
        updated_values = {'status': status, 'academic_year': admission_year}
        
        # Use the Hostel instance in update_or_create
        obj, created = HostelAttendance.objects.update_or_create(
            name=hostel_instance, 
            attendance_date=attendance_date, 
            defaults=updated_values
        )
        return JsonResponse({'msg': 'success'})
    except StudentProfile.DoesNotExist:
        return JsonResponse({'msg': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'msg': 'Error', 'details': str(e)}, status=500)


# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
@csrf_exempt
def saveStaffAttendance(request):
    id = request.POST.get('id')
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    status = request.POST.get('value')
    staff = StaffProfile.objects.get(id=id)
    attendance_date = date.today()

    updated_values = {'status': status,'academic_year':admission_year}


    obj, created = StaffAttendance.objects.update_or_create(
        name=staff, attendance_date=attendance_date,defaults=updated_values
    )
    return JsonResponse({'msg':'success'})

# Create your views here.
def get_last_seven_days_stu_attendance(studentList, admission_year):
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_seven_days = [yesterday - timedelta(days=i) for i in range(7)]
    
    # Correctly filter holiday dates
    holiday_dates = Holiday.objects.filter(
        holiday_date__in=last_seven_days, 
        academic_year=admission_year
    ).values_list('holiday_date', flat=True)

    attendance_data = {}

    for student in studentList:
        records = []
        for day in last_seven_days:
            if day in holiday_dates:
                records.append('holiday')
            elif day.weekday() == 5:  # Saturday (5) or Sunday (6)
                records.append('weekend')
            else:
                record = StudentAttendance.objects.filter(
                    name=student, attendance_date=day
                ).first()
                if record:
                    records.append(record.status)
                else:
                    records.append(None)
        attendance_data[student.id] = records
    
    return attendance_data

# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user,"teacher", roles=['Manager','HR']))
def studentAttendance(request):
    admission_year_list = Admission_Year.objects.all().order_by("-id")
    session_year_list = AcademicSession.objects.all().order_by("-id")
    classList = ClassConfig.objects.all()
    studentList = None
    attendance_date = date.today().strftime('%Y-%m-%d')
    
    class_group_mapping = {}
    for class_config in ClassConfig.objects.select_related('class_group_id'):
        has_group = class_config.class_group_id and class_config.class_group_id.group_id is not None
        class_group_mapping[class_config.id] = has_group

    # Serialize the mapping to JSON
    class_group_mapping_json = json.dumps(class_group_mapping)

    if request.method == 'POST':
        class_id = request.POST.get('class_name_id')
        admission_year_id = request.POST.get('admission_year_id')
        session_year_id = request.POST.get('session_year_id')
        studentList = StudentProfile.objects.filter(
            Q(class_id=class_id) &
            Q(admission_year_id=admission_year_id) &
            (Q(academic_session_year=session_year_id) | Q(academic_session_year__isnull=True)) &
            Q(student_field__status="Active")).order_by("roll_no")

    attendance_data = get_last_seven_days_stu_attendance(studentList, admission_year_id) if studentList else {}

    context = {
        'admission_year_list':admission_year_list,
        'session_year_list':session_year_list,
        'studentList': studentList,
        'classList': classList,
        'attendance_date': attendance_date,
        'heading': 'Attendance',
        'subheading': 'Student Attendance',
        'class_group_mapping': class_group_mapping_json,
        'attendance_data': attendance_data
    }

    return render(request, 'attendance/studentattendance.html', context) 

# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user,"teacher", roles=['Manager','HR']))
@csrf_exempt 
def get_student_attendance(request):
    date = request.POST.get('date')
    studentattend=StudentAttendance.objects.filter(attendance_date=date)
    studentattendlist=list(studentattend.values('name','status'))
    return JsonResponse({"attendance": studentattendlist})


def get_last_seven_days_hostel_attendance(studentList, admission_year):
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_seven_days = [yesterday - timedelta(days=i) for i in range(7)]
    attendance_data = {}

    for student in studentList:
        # Fetch the related Hostel instance for the student
        hostel_instance = Hostel.objects.filter(student_id=student, academic_year=admission_year).first()
        if not hostel_instance:
            # If no Hostel instance is found, skip this student
            attendance_data[student.id] = ['No hostel record'] * len(last_seven_days)
            continue

        records = []
        for day in last_seven_days:
            record = HostelAttendance.objects.filter(
                name=hostel_instance, attendance_date=day
            ).first()
            if record:
                records.append(record.status)
            else:
                records.append(None)
        attendance_data[student.id] = records

    return attendance_data

# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user,"student", roles=['Manager','HR']))
def studentHostelAttendance(request): 
    current_year = str(date.today().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    hostel_student_instance = Hostel.objects.filter(academic_year=admission_year)
    student_ids = hostel_student_instance.values_list('student_id', flat=True)
    studentList = StudentProfile.objects.filter(
        Q(
            academic_session_year__start_year__lte=admission_year.name,
            academic_session_year__end_year__gte=admission_year.name
        ) |
        Q(admission_year_id=admission_year),
        id__in=student_ids
    )
    attendance_date = date.today().strftime('%Y-%m-%d')

    # Build the attendance data dictionary
    attendance_data = {}
    for student in studentList:
        attendance_records = HostelAttendance.objects.filter(
            name__student_id=student,
            attendance_date__lte=date.today(),
            attendance_date__gte=date.today() - timedelta(days=7)
        ).values_list('status', flat=True)
        attendance_data[student.id] = list(attendance_records)

    context = {
        'studentList': studentList,
        'attendance_date': attendance_date,
        'attendance_data': attendance_data,
        'heading': 'Attendance',
        'subheading': 'Hostel Attendance',
    }

    return render(request, 'attendance/student_hostel_attendance.html', context)


# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))

@csrf_exempt 
def get_hostel_student_attendance(request):
    date = request.POST.get('date')
    student_attendances = HostelAttendance.objects.filter(attendance_date=date)
    studentattendlist = [
        {'student_id': attendance.name.student_id.id, 'status': attendance.status}
        for attendance in student_attendances
    ]
    print(studentattendlist)
    return JsonResponse({"attendance": studentattendlist})



# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user, "student", "parent", roles=['Manager','HR']))
def report_student_attendance(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    classList = ClassConfig.objects.all()
    session_year_list = AcademicSession.objects.all()
    condensed_data = []
    condensed_data_sorted = None
    holidays = []
    class_name = None
    requested_user =None
    admission_session_instance=None

    weekend_days_qs = WeekendDay.objects.filter(academic_year=admission_year)
    
    # Map short day codes ('sat', 'fri', etc.) to JavaScript-style 0-6 index
    DAYS_MAPPING = {
        "sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6
    }

    weekend_days = [DAYS_MAPPING[weekend.day] for weekend in weekend_days_qs if weekend.day in DAYS_MAPPING]

    if request.user.is_authenticated and is_staff_or_has_role(request.user,"student", "parent", roles=["Manager", "HR"]):
        requested_user = request.user


    if request.method == 'POST':
        month = request.POST.get('searchMonth')
        class_id = request.POST.get('class_name_id')
        admission_session = request.POST.get('session_year_id')

        try:
            admission_session_instance = AcademicSession.objects.get(id=admission_session)
        except AcademicSession.DoesNotExist:
            admission_session_instance = None
        if class_id:
            class_name= ClassConfig.objects.get(id=class_id)
        search_date = datetime.strptime(month, '%Y-%m').date()

        if requested_user.groups.filter(name='student').exists():
            attendance_records = StudentAttendance.objects.filter(
                name__student_field=requested_user,
                attendance_date__year=search_date.year,
                attendance_date__month=search_date.month
            )

        elif requested_user.groups.filter(name='parent').exists(): 
            children_profiles = StudentProfile.objects.filter(parent_id=requested_user)
            children = [child_profile.student_field for child_profile in children_profiles]

            
            attendance_records = StudentAttendance.objects.filter( 
                name__student_field__in=children,
                attendance_date__year=search_date.year,
                attendance_date__month=search_date.month
            )

        else:
            attendance_records = StudentAttendance.objects.filter(
                attendance_date__year=search_date.year,
                attendance_date__month=search_date.month,
                name__class_id=class_id,
                name__academic_session_year=admission_session
            )

        attendancelist = list(attendance_records.values('name__student_field__name','name__roll_no', 'name__student_field__user_id', 'status', 'attendance_date'))

        # Group attendance records by student name
        grouped_attendance = {name: list(group) for name, group in groupby(attendancelist, key=itemgetter('name__student_field__name'))}

        
        for name, records in grouped_attendance.items():
            attendance_dates = [record['attendance_date'].day for record in records if record['status']]
            roll_no = records[0].get('name__roll_no') or records[0].get('name__student_field__user_id')
            condensed_data.append({'name': name, 'roll_no': roll_no, 'attendance': attendance_dates})


        holiday_records = Holiday.objects.filter(
            holiday_date__year=search_date.year,
            holiday_date__month=search_date.month
        )
        holidaylist = list(holiday_records.values('holiday_date'))

        holidays = [date['holiday_date'].day for date in holidaylist]

        condensed_data_sorted = sorted(condensed_data, key=lambda x: x['roll_no'])

    context = {
        'classList': classList,
        'session_year_list':session_year_list,
        'heading': 'Attendance Report',
        'subheading': 'Student Monthly Attendance',
        'attendanceData': condensed_data_sorted,
        'holidayData': holidays,
        'class_name':class_name,
        'admission_session':admission_session_instance,
        'weekendDays': weekend_days 
    }
    return render(request, 'attendance/report/student_attend_report.html', context)  


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def report_date_student_attendance(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    datewise_attendance_counts = None
    total_student = None
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Query StudentAttendance instances within the specified date range
        attendances = StudentAttendance.objects.filter(
            Q(attendance_date__gte=start_date) & Q(attendance_date__lte=end_date) & Q(academic_year=admission_year)
        )
        # total_student=StudentProfile.objects.filter(Q(student_field__status="Active") & Q(admission_year_id=admission_year)).count()
        total_student = StudentProfile.objects.filter(Q(
            academic_session_year__start_year__lte=admission_year.name,
            academic_session_year__end_year__gte=admission_year.name
        ) |
        Q(admission_year_id=admission_year) & Q(student_field__status="Active")).count()
        # Count attendances for each student
        datewise_attendance_counts = attendances.values('attendance_date').annotate(
            total_students=Count('name', distinct=True),
            present_students=Count(
                Case(When(status=True, then=1), output_field=IntegerField())
            ),
        )

        datewise_attendance_counts = datewise_attendance_counts.annotate(
            absent_students=Value(total_student, output_field=IntegerField()) - F('present_students')
        )


    context = {
        'total_student':total_student,
        'datewise_attendance_counts': datewise_attendance_counts,
        'heading': 'Attendance Report',
        'subheading': 'Student Date Range Attendance',
    }
    return render(request, 'attendance/report/student_date_report.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def report_time_student_attendance(request):
    
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    class_list =ClassConfig.objects.all()
    attendance_records=None
    search_date=None
    present_count=None
    absent_count=None
    if request.method == 'POST': 
        date = request.POST.get('date')
        search_date = datetime.strptime(date, '%Y-%m-%d').date()
        class_id = request.POST.get('class_id')
        class_name= ClassConfig.objects.get(id=class_id)
        total_student=StudentProfile.objects.filter(Q(student_field__status="Active") & Q(admission_year_id=admission_year) & Q(class_id=class_name)).count()
        attendance_records = StudentAttendance.objects.filter(
            Q(attendance_date=search_date) &  
            Q(name__class_id=class_name)    
        ).order_by("name__roll_no")

        students_with_attendance = StudentAttendance.objects.filter(
            Q(attendance_date=search_date) &  
            Q(name__class_id=class_name) 
        ).values('name')
        
        students_without_attendance = StudentProfile.objects.filter(
            admission_year_id=admission_year,
            class_id=class_name
        ).exclude(id__in=Subquery(students_with_attendance.values('name')))


        if total_student !=students_without_attendance.count():
            
            with transaction.atomic():
                for student in students_without_attendance:
                    # Check if there is an existing attendance record for the student on the specified date
                    attendance_record = StudentAttendance.objects.filter(
                        name=student,
                        attendance_date=search_date,
                        academic_year=admission_year
                    ).first()
                    
                    if not attendance_record:
                        StudentAttendance.objects.create(
                            name=student,
                            status=False,
                            attendance_date=search_date,
                            academic_year=admission_year
                        )


        present_count = attendance_records.filter(status=True).count()
        absent_count = total_student - present_count

    
    context = {
        'search_date':search_date,
        'class_list':class_list,
        'present_count':present_count,
        'absent_count':absent_count,
        'attendance_records':attendance_records,
        'heading': 'Attendance Report',
        'subheading': 'Student Time Wize Attendance',
    }
    return render(request, 'attendance/report/student_time_report.html', context)



def get_last_seven_days_staff_attendance(staff_list, admission_year):
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_seven_days = [yesterday - timedelta(days=i) for i in range(7)]
    
    # Fix: Directly compare holiday_date with last_seven_days
    holiday_dates = Holiday.objects.filter(
        holiday_date__in=last_seven_days,  # Corrected comparison
        academic_year=admission_year
    ).values_list('holiday_date', flat=True)

    attendance_data = {}

    for staff in staff_list:
        records = []
        for day in last_seven_days:
            if day in holiday_dates:
                records.append('holiday')
            elif day.weekday() in [5, 6]:  # Saturday (5) or Sunday (6)
                records.append('weekend')
            else:
                record = StaffAttendance.objects.filter(
                    name=staff, attendance_date=day
                ).first()
                if record:
                    records.append(record.status)
                else:
                    records.append(None)
        attendance_data[staff.id] = records
    
    return attendance_data

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def staffAttendance(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    attendance_date = date.today().strftime('%Y-%m-%d')
    stafflist=StaffProfile.objects.filter(staff_field__status="Active")
    attendance_data = get_last_seven_days_staff_attendance(stafflist, admission_year)
    context={
        'stafflist':stafflist,
        'attendance_date':attendance_date,
        'attendance_data':attendance_data,
        'heading': 'Attendance',
        'subheading': 'Staff Attendance',
    }

    return render (request,'attendance/staffattendance.html',context) 
 
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
@csrf_exempt 
def get_staff_attendance(request):
    date = request.POST.get('date')
    staffattend=StaffAttendance.objects.filter(attendance_date=date)
    staffattendlist=list(staffattend.values('name','status'))
    return JsonResponse({"attendance": staffattendlist}) 

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, "staff", roles=['Manager','HR', 'Accountant']))
def report_staff_attendance(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)

    condensed_data = []
    holidays = []
    search_date = None
    requested_user=None

    weekend_days_qs = WeekendDay.objects.filter(academic_year=admission_year)
    
    # Map short day codes ('sat', 'fri', etc.) to JavaScript-style 0-6 index
    DAYS_MAPPING = {
        "sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6
    }

    weekend_days = [DAYS_MAPPING[weekend.day] for weekend in weekend_days_qs if weekend.day in DAYS_MAPPING]


    if request.user.is_authenticated and is_staff_or_has_role(request.user,"staff",  roles=["Manager", "HR", "Accountant"]):
        requested_user = request.user

    if request.method == 'POST':
        month = request.POST.get('searchMonth')
        search_date = datetime.strptime(month, '%Y-%m').date()

        if is_staff_or_has_role(request.user, roles=["Manager", 'HR']):
                attendance_records = StaffAttendance.objects.filter(
                    attendance_date__year=search_date.year,
                    attendance_date__month=search_date.month
                )
        else:
            attendance_records = StaffAttendance.objects.filter(
                name__staff_field=requested_user,
                attendance_date__year=search_date.year,
                attendance_date__month=search_date.month
            )
        
        attendancelist = list(attendance_records.values('name__staff_field__name','name__staff_field__user_id', 'status', 'attendance_date'))
        grouped_attendance = {name: list(group) for name, group in groupby(attendancelist, key=itemgetter('name__staff_field__name'))}

        for name, records in grouped_attendance.items():
            attendance_dates = [record['attendance_date'].day for record in records if record['status']]
            user_id = records[0]['name__staff_field__user_id']
            condensed_data.append({'name': name, 'user_id': user_id, 'attendance': attendance_dates})


        holiday_records = Holiday.objects.filter(
            holiday_date__year=search_date.year,
            holiday_date__month=search_date.month
        )
        holidaylist = list(holiday_records.values('holiday_date'))

        holidays = [date['holiday_date'].day for date in holidaylist]

    context = {
        'heading': 'Attendance Report',
        'subheading': 'Staff Attendance',
        'attendanceData': condensed_data,
        'holidayData': holidays,
        'search_date': search_date,
        'requested_user': requested_user,
        'weekendDays': weekend_days 
    }
    return render(request, 'attendance/report/staff_attend_report.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def report_time_staff_attendance(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    attendance_records=None
    search_date=None
    present_count=None
    absent_count=None
    if request.method == 'POST': 
        date = request.POST.get('date')
        search_date = datetime.strptime(date, '%Y-%m-%d').date()
        total_staff=StaffProfile.objects.filter(Q(staff_field__status="Active")).count()
        attendance_records = StaffAttendance.objects.filter(
            Q(attendance_date=search_date) 
        )


        staff_with_attendance = StaffAttendance.objects.filter(
            Q(attendance_date=search_date)
        ).values('name')
        
        staff_without_attendance = StaffProfile.objects.filter(
            staff_field__status="Active"
        ).exclude(id__in=Subquery(staff_with_attendance.values('name')))

        if total_staff !=staff_without_attendance.count():
            with transaction.atomic():
                for staff in staff_without_attendance:
                    # Check if there is an existing attendance record for the student on the specified date
                    attendance_record = StaffAttendance.objects.filter(
                        name=staff,
                        attendance_date=search_date
                    ).first()
                    
                    if not attendance_record:
                        StaffAttendance.objects.create(
                            name=staff,
                            status=False,
                            attendance_date=search_date,
                            academic_year=admission_year
                        )
        present_count = attendance_records.filter(status=True).count()
        absent_count = total_staff - present_count

    context = {
        'search_date':search_date,
        'present_count':present_count,
        'absent_count':absent_count,
        'attendance_records':attendance_records,
        'heading': 'Attendance Report',
        'subheading': 'Teacher Time Wize Attendance',
    }
    return render(request, 'attendance/report/staff_time_report.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def leave_quota(request):
    context={
        'heading':'Attendance',
        'subheading':'Leave Type',
    }
    return render(request, 'attendance/leave_quota/leave_quota.html',context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_leave_quota(request):
    leavequotalist = LeaveQuota.objects.all()
    context = {
        'leavequotalist': leavequotalist
    }
    return render(request, 'attendance/leave_quota/list_leave_quota.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_leave_quota(request):
    if request.method == 'POST':
        form = LeaveQuotaform(request.POST)
        if form.is_valid():
            leave_quota = form.save(commit=False)
            if leave_quota.working_hour is None:
                leave_quota.working_hour = 0.0
            leave_quota.save()
            messages.success(request, 'Leave Quota has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "leavequotaListChanged": "leavequotaListChanged"
                })})
        
    else:
        form = LeaveQuotaform()

    context = {
        'form': form
    } 

    return render(request, 'attendance/leave_quota/add_leave_quota.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_leave_quota(request, pk):
    leave_quota = get_object_or_404(LeaveQuota, pk=pk)
    if request.method == 'POST':
        form = LeaveQuotaform(request.POST, instance=leave_quota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave quota has been updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "leavequotaListChanged": "leavequotaListChanged"
                })})
            
    else:
        form = LeaveQuotaform(instance=leave_quota)

    context = {
        'form': form
    }

    return render(request, 'attendance/leave_quota/add_leave_quota.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_leave_quota(request, pk):
    leave_quota = get_object_or_404(LeaveQuota, pk=pk)
    leave_quota.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'leavequotaListChanged'})


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def leave_type(request):
    context={
        'heading':'Attendance',
        'subheading':'Leave Type',
    }
    return render(request, 'attendance/leavetype/leave_type.html',context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_leave_type(request):
    leavetypelist = LeaveType.objects.all()
    context = {
        'leavetypelist': leavetypelist
    }
    return render(request, 'attendance/leavetype/list_leave_type.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_leave_type(request):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave type has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "leavetypeListChanged": "leavetypeListChanged"
                })})
           
    else:
        form = LeaveTypeForm()

    context = {
        'form': form
    }

    return render(request, 'attendance/leavetype/add_leave_type.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_leave_type(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave type has been Edited ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "leavetypeListChanged": "leavetypeListChanged"
                })})
            
    else:
        form = LeaveTypeForm(instance=leave_type)

    context = {
        'form': form
    }

    return render(request, 'attendance/leavetype/add_leave_type.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_leave_type(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)
    leave_type.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'leavetypeListChanged'})



@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"teacher","parent","student","staff", roles=['Manager','HR','Accountant']))
def leave_request(request):
    context={
        'heading':'Attendance',
        'subheading':'Leave Request',
    }
    return render(request, 'attendance/leaverequest/leave_request.html',context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"teacher","parent","student","staff", roles=['Manager','HR','Accountant']))
def list_leave_request(request):
    current_user=request.user
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    if is_staff_or_has_role(request.user,  roles=["Manager", 'HR']):
        leaverequestlist = LeaveRequest.objects.filter(academic_year=admission_year).order_by("-id")
    elif current_user.groups.filter(name='parent').exists():
        children_profiles = Student.objects.filter(student_profile__parent_id=current_user)
        leaverequestlist = LeaveRequest.objects.filter(Q(academic_year=admission_year) & Q(employee__in=children_profiles)).order_by("-id")
    else:
        leaverequestlist = LeaveRequest.objects.filter(Q(academic_year=admission_year) & Q(employee=current_user)).order_by("-id")
    context = {
        'leaverequestlist': leaverequestlist
    }
    return render(request, 'attendance/leaverequest/list_leave_request.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"teacher","parent","student","staff", roles=['Manager','HR','Accountant']))
def add_leave_request(request):
    current_user = request.user
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    list_leave_type = LeaveType.objects.all()
    staff_list = CustomUser.objects.filter(status="Active", staff_profile__isnull=False)
    student_list = Student.objects.filter(
    Q(
        student_profile__academic_session_year__start_year__lte=admission_year.name,
        student_profile__academic_session_year__end_year__gte=admission_year.name
    ) |
    Q(student_profile__admission_year_id=admission_year), status="Active")

    working_hour = 8

    user_list = []

    if is_staff_or_has_role(request.user, roles=['Manager', 'HR', 'Accountant']):
        user_list = list(chain(staff_list, student_list))
    elif current_user.groups.filter(name='parent').exists():
        children_profiles = Student.objects.filter(student_profile__parent_id=current_user)
        user_list = [child_profile for child_profile in children_profiles]

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        user = get_object_or_404(CustomUser, pk=employee_id) if employee_id else current_user
        leave_type_id = request.POST.get('leave_type')
        leave_type_instance = get_object_or_404(LeaveType, pk=leave_type_id)
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
        start_hour_str = request.POST.get('start_hour')
        end_hour_str = request.POST.get('end_hour')
        start_hour = datetime.strptime(start_hour_str, '%H:%M').time() if start_hour_str else None
        end_hour = datetime.strptime(end_hour_str, '%H:%M').time() if end_hour_str else None

        group = user.groups.first()
        if not group:
            messages.error(request, "The selected user does not belong to any group.")
            return redirect("leave_request")

        try:
            quota=LeaveQuota.objects.get(group=group)
            quota_limit=quota.leave_days_limit
        except LeaveQuota.DoesNotExist:
            messages.error(request, f"No LeaveQuota is defined for the group {group.name}.")
            return redirect("leave_request")
        
        # Check if it's hourly leave
        if start_hour and end_hour:
            start_datetime = datetime.combine(start_date, start_hour)
            end_datetime = datetime.combine(end_date, end_hour)
            duration = end_datetime - start_datetime
            total_hours = duration.total_seconds() / 3600  # Convert seconds to hours
            equivalent_days = total_hours / working_hour  # Convert hours to equivalent days
        else:
            duration = end_date - start_date
            equivalent_days = duration.days + 1  # Include the start date

        print("equivalent_days",equivalent_days)

        approved_leaves = LeaveRequest.objects.filter(
            employee=user,
            status='Approved',
            academic_year=admission_year,
            leave_type__is_special=False
        )

        # Calculate total hours for hourly leaves
        total_approved_hours = 0
        hourly_leaves = approved_leaves.filter(
            start_hour__isnull=False,
            end_hour__isnull=False
        )

        for leave in hourly_leaves:
            start_datetime = datetime.combine(leave.start_date, leave.start_hour)
            end_datetime = datetime.combine(leave.end_date, leave.end_hour)
            duration = end_datetime - start_datetime
            total_approved_hours += duration.total_seconds() / 3600  # Convert seconds to hours

        # Calculate total days for non-hourly leaves
        total_approved_days_non_hourly = approved_leaves.filter(
            Q(start_hour__isnull=True) & Q(end_hour__isnull=True)
        ).annotate(
            duration_in_days=ExpressionWrapper(
                F('end_date') - F('start_date') + timedelta(days=1),
                output_field=DurationField()
            )
        ).aggregate(
            total_days=Sum('duration_in_days')
        )['total_days']

        if total_approved_days_non_hourly is None:
            total_approved_days_non_hourly = 0
        elif isinstance(total_approved_days_non_hourly, timedelta):
            total_approved_days_non_hourly = total_approved_days_non_hourly.days

        # Combine hourly leaves (converted to equivalent days) and non-hourly leaves
        total_approved_days = total_approved_days_non_hourly + (total_approved_hours / working_hour)

        # Debug output
        print(f"Total approved days (including hourly): {total_approved_days}")

        
        leave_request = LeaveRequest(
            employee=user,
            start_date=start_date,
            end_date=end_date,
            start_hour=start_hour,
            end_hour=end_hour,
            leave_type=leave_type_instance,
            status='Pending',
            academic_year=admission_year,
            created_by=request.user,
        )
        total_approved_days_decimal = Decimal(total_approved_days)

        if leave_type_instance.is_special:
            # For special leave, bypass the quota check
            leave_request.save()
            messages.success(request, 'Special Leave Request sent successfully!')
        else:
            # For regular leave, check against the quota
            if total_approved_days_decimal + Decimal(equivalent_days) > quota_limit:
                total_day_left = quota_limit - total_approved_days_decimal
                messages.error(request, f'You have {total_day_left} days left.')
            else:
                leave_request.save()
                messages.success(request, 'Leave Request sent successfully!')

        return redirect("leave_request")


    context = {
        'heading': 'Attendance',
        'subheading': 'Leave Request',
        'list_leave_type': list_leave_type,
        'user_list': user_list,
    }

    return render(request, 'attendance/leaverequest/add_leave_request.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_leave_request(request, pk):
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request has been edited successfully!')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "leaverequestListChanged": "leaverequestListChanged"
                })})
        else:
            print(form.errors)
    else:
        form = LeaveRequestForm(instance=leave_request)
    
    context = {
        'form': form
    }
    
    return render(request, 'attendance/leaverequest/edit_leave_request.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_leave_request(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    leave_request.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'leaverequestListChanged'})


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
@csrf_exempt
def change_leave_status(request):
    if request.method == 'POST':
        leave_request_id = request.POST.get('id')
        status = request.POST.get('status')
        print(status)
        try:
            leave_request = LeaveRequest.objects.get(id=leave_request_id)
            leave_request.status = status
            leave_request.save()
            return JsonResponse({'success': True})
        except LeaveRequest.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Leave request not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def holiday(request):
    context = {
        'heading': 'Attendance',
        'subheading': 'Holiday Name',
    }
    return render(request, 'attendance/holiday/holiday.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_holiday(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    holidayList = Holiday.objects.filter(
        academic_year=admission_year
    )
    context = {
        'holidayList': holidayList
    }
    return render(request, 'attendance/holiday/holiday_list.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_holiday(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    form = Holidayform(initial={'academic_year': admission_year})
    if request.method == 'POST':
        form = Holidayform(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Holiday Name has been saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "holidayListChanged": "holidayListChanged"
                })})
    
    context = {
        'form': form
    }

    return render(request, 'attendance/holiday/add_holiday.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_holiday(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        form = Holidayform(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, 'Holiday Name has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "holidayListChanged": "holidayListChanged"
                })})
    else:
        form = Holidayform(instance=holiday)

    context = {
        'form': form
    }

    return render(request, 'attendance/holiday/add_holiday.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_holiday(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    holiday.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'holidayListChanged'})


