from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from .forms import *
from .models import *
from attendance.models import StudentAttendance,StaffAttendance
from core.models import StudentClass
from miscellaneous.models import Event,Institute
from crucial.models import Expenseitemlist,Fees,SMSUsage,TeacherSubjectAssign,Notice
from django.core.exceptions import ObjectDoesNotExist
from user.models import Student, StaffProfile,StaffProfile,ParentProfile,StudentProfile
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from user.decorators import *
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.utils import timezone
from datetime import date,datetime
from django.db.models import Sum, Q, F, Value, FloatField, Case, When, Count
from django.forms import inlineformset_factory
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from exam.models import Forth_Sub
from django.forms import ValidationError

# Create your views here.

# Create your views here.
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, "teacher", "staff","parent","student", roles=['Manager', 'Accountant']))
def dashboard(request):
    if is_staff_or_has_role(request.user, "teacher", "staff","parent","student", roles=["Manager", 'Accountant']):
        requested_user = request.user
        current_date = timezone.now().date()
        current_datetime = timezone.now()
        t_student_attend=None
        t_staff_attend=None
        upcoming_events=None
        upcoming_notices=None
        masking_limit=None
        nonmasking_limit=None
        heading = 'Dashboard'

        academic_year = Admission_Year.objects.latest('updated_at') if Admission_Year.objects.exists() else None
        academic_year_list = Admission_Year.objects.all()

        # Calculate Total Counts
        totalTeachers = StaffProfile.objects.filter(Q(staff_field__status="Active")).count()
        totalStaffs = StaffProfile.objects.filter(Q(staff_field__status="Active")).count()
        totalStudents = StudentProfile.objects.filter(Q(student_field__status="Active")
        ).count()
        totalParents = ParentProfile.objects.filter(
            Q(parent_field__std_parent__student_field__status="Active")
        ).distinct().count()

        # Attendance Counts
        t_student_attend = StudentAttendance.objects.filter(Q(attendance_date=current_date) & Q(status=True)).count()
        t_staff_attend = StaffAttendance.objects.filter(Q(attendance_date=current_date) & Q(status=True)).count()

        # Absentees
        t_student_absent = totalStudents - t_student_attend
        t_staff_absent = totalStaffs - t_staff_attend

        # SMS Usage
        masking_limit = SMSUsage.objects.filter(Msg_type='MASKING').first()
        nonmasking_limit = SMSUsage.objects.filter(Msg_type='NONMASKING').first()

        # Gender Counts
        male_students = StudentProfile.objects.filter(
            Q(student_field__status="Active") & Q(student_field__gender="Male") & Q(admission_year_id=academic_year)
        ).count()
        female_students = StudentProfile.objects.filter(
            Q(student_field__status="Active") & Q(student_field__gender="Female") & Q(admission_year_id=academic_year)
        ).count()

        # Notices and Events
        upcoming_notices = Notice.objects.filter(Q(date__gte=current_date)).order_by('date')[:3]
        upcoming_events = Event.objects.filter(Q(start__gte=current_datetime)).order_by('start')[:3]

        male_staffs= StaffProfile.objects.filter(Q(staff_field__status='Active') & Q(staff_field__gender="Male")).count()
        female_staffs= StaffProfile.objects.filter(Q(staff_field__status='Active') & Q(staff_field__gender="Female")).count()
            

        if has_role(requested_user, ["Manager"]):

            context = {
                'heading': heading,
                'totalStaffs':totalStaffs,
                'totalStudents':totalStudents,
                'male_students':male_students,
                'male_employees':male_staffs,
                'female_employees':female_staffs,
                'female_students':female_students,
                'totalParents':totalParents,
                't_student_attend':t_student_attend,
                't_student_absent':t_student_absent,
                't_staff_attend':t_staff_attend,
                't_staff_absent':t_staff_absent,
                'masking_limit':masking_limit,
                'nonmasking_limit':nonmasking_limit,
                'upcoming_notices':upcoming_notices,
                'upcoming_events':upcoming_events,
                'academic_year': academic_year,
                'academic_year_list': academic_year_list,
                    }
            return render(request, 'userdash/manager.html', context)
        
        elif has_role(requested_user, ["Accountant"]):
            context = {
                'heading': heading,
                'totalStaffs':totalStaffs,
                'totalStudents':totalStudents,
                'male_students':male_students,
                'male_employees':male_staffs,
                'female_employees':female_staffs,
                'female_students':female_students,
                'totalParents':totalParents,
                't_student_attend':t_student_attend,
                't_student_absent':t_student_absent,
                't_staff_attend':t_staff_attend,
                't_staff_absent':t_staff_absent,
                'masking_limit':masking_limit,
                'nonmasking_limit':nonmasking_limit,
                'upcoming_notices':upcoming_notices,
                'upcoming_events':upcoming_events,
                'academic_year': academic_year,
                'academic_year_list': academic_year_list,
                }
            return render(request, 'userdash/accountant.html', context)
        
        elif has_role(requested_user, ["HR"]):
            
            context = {
                'heading': heading,
                'totalStaffs':totalStaffs,
                'totalStudents':totalStudents,
                'male_students':male_students,
                'male_employees':male_staffs,
                'female_employees':female_staffs,
                'female_students':female_students,
                'totalParents':totalParents,
                't_student_attend':t_student_attend,
                't_student_absent':t_student_absent,
                't_staff_attend':t_staff_attend,
                't_staff_absent':t_staff_absent,
                'masking_limit':masking_limit,
                'nonmasking_limit':nonmasking_limit,
                'upcoming_notices':upcoming_notices,
                'upcoming_events':upcoming_events,
                'academic_year': academic_year,
                'academic_year_list': academic_year_list,
                }
            return render(request, 'userdash/hr.html', context)
        
        elif requested_user.groups.filter(name='teacher').exists():

            context = {
                'heading': heading,
                'upcoming_notices':upcoming_notices,
                'upcoming_events':upcoming_events
                }
            return render(request, 'userdash/teacher.html', context)
        
        elif requested_user.groups.filter(name='staff').exists():

            context = {
                'heading': heading,
                'upcoming_notices':upcoming_notices,
                'upcoming_events':upcoming_events
                }
            return render(request, 'userdash/staff.html', context)
        
        elif requested_user.groups.filter(name='student').exists():
            
            context = {
                'heading': heading,
                'upcoming_notices':upcoming_notices,
                'upcoming_events':upcoming_events
                }
            return render(request, 'userdash/student.html', context)
        
        elif requested_user.groups.filter(name='parent').exists():
            
            context = {
                'heading': heading,
                'upcoming_notices':upcoming_notices,
                'upcoming_events':upcoming_events
                    }
            return render(request, 'userdash/parent.html', context)
    
    
    context = {
        'heading': heading,
        'totalStaffs':totalStaffs,
        'totalStudents':totalStudents,
        'male_students':male_students,
        'male_employees':male_staffs,
        'female_employees':female_staffs,
        'female_students':female_students,
        'totalParents':totalParents,
        't_student_attend':t_student_attend,
        't_student_absent':t_student_absent,
        't_staff_attend':t_staff_attend,
        't_staff_absent':t_staff_absent,
        'masking_limit':masking_limit,
        'nonmasking_limit':nonmasking_limit,
        'upcoming_notices':upcoming_notices,
        'upcoming_events':upcoming_events,
        'academic_year': academic_year,
        'academic_year_list': academic_year_list,
        }
    return render(request, 'index.html', context)


# def dashboard(request):
#     user = request.user
#     heading = "Dashboard"
#     current_date = datetime.now().date()
#     current_datetime = datetime.now()

#     # Fetch academic year details
#     academic_year = Admission_Year.objects.latest('updated_at') if Admission_Year.objects.exists() else None
#     academic_year_list = Admission_Year.objects.all()

#     # Calculate Total Counts
#     totalTeachers = StaffProfile.objects.filter(Q(staff_field__status="Active")).count()
#     totalStaffs = StaffProfile.objects.filter(Q(staff_field__status="Active")).count()
#     totalStudents = StudentProfile.objects.filter(
#         Q(admission_year_id=academic_year) & Q(student_field__status="Active")
#     ).count()
#     totalParents = ParentProfile.objects.filter(
#         Q(parent_field__std_parent__admission_year_id=academic_year.id) & 
#         Q(parent_field__std_parent__student_field__status="Active")
#     ).distinct().count()

#     # Attendance Counts
#     t_student_attend = StudentAttendance.objects.filter(Q(attendance_date=current_date) & Q(status=True)).count()
#     t_staff_attend = StaffAttendance.objects.filter(Q(attendance_date=current_date) & Q(status=True)).count()

#     # Absentees
#     t_student_absent = totalStudents - t_student_attend
#     t_staff_absent = totalStaffs - t_staff_attend

#     # SMS Usage
#     masking_limit = SMSUsage.objects.filter(Msg_type='MASKING').first()
#     nonmasking_limit = SMSUsage.objects.filter(Msg_type='NONMASKING').first()

#     # Gender Counts
#     male_students = StudentProfile.objects.filter(
#         Q(student_field__status="Active") & Q(student_field__gender="Male") & Q(admission_year_id=academic_year)
#     ).count()
#     female_students = StudentProfile.objects.filter(
#         Q(student_field__status="Active") & Q(student_field__gender="Female") & Q(admission_year_id=academic_year)
#     ).count()

#     # Notices and Events
#     upcoming_notices = Notice.objects.filter(Q(date__gte=current_date)).order_by('date')[:3]
#     upcoming_events = Event.objects.filter(Q(start__gte=current_datetime)).order_by('start')[:3]

#     male_staffs= StaffProfile.objects.filter(Q(staff_field__status='Active') & Q(staff_field__gender="Male")).count()
#     female_staffs= StaffProfile.objects.filter(Q(staff_field__status='Active') & Q(staff_field__gender="Female")).count()
#     context = {
#         'heading': heading,
#         'totalTeachers': totalTeachers,
#         'totalStaffs': totalStaffs,
#         'totalStudents': totalStudents,
#         'totalParents': totalParents,
#         't_student_attend': t_student_attend,
#         't_student_absent': t_student_absent,
#         't_staff_attend': t_staff_attend,
#         't_staff_absent': t_staff_absent,
#         'masking_limit': masking_limit,
#         'nonmasking_limit': nonmasking_limit,
#         'male_students': male_students,
#         'female_students': female_students,
#         'male_employees':male_staffs,
#         'female_employees':female_staffs,
#         'upcoming_notices': upcoming_notices,
#         'upcoming_events': upcoming_events,
#         'academic_year': academic_year,
#         'academic_year_list': academic_year_list,
#     }

#     if user.is_superuser:
#         return render(request, 'index.html', context)

#     elif user.groups.filter(name='staff').exists():
#         staff_profile = StaffProfile.objects.filter(staff_field=user).first()
#         staff_role = staff_profile.role.name.lower() if staff_profile and staff_profile.role else None

#         staff_templates = {
#             "manager": "userdash/manager.html",
#             "accountant": "userdash/accountant.html",
#         }

#         return render(request, staff_templates.get(staff_role, 'userdash/staff.html'), context)

#     elif user.groups.filter(name='student').exists():
#         return render(request, 'userdash/student.html', context)

#     elif user.groups.filter(name='parent').exists():
#         return render(request, 'userdash/parent.html', context)

#     return render(request, 'index.html', context)

# def auth_login(request):
#     if request.method == 'POST':
#         identifier = request.POST.get('username')  # Username or Phone Number
#         password = request.POST.get('password')

#         from django.contrib.auth import get_user_model
#         User = get_user_model()

#         # Find user by phone number or username
#         user_obj = User.objects.filter(Q(phone_number=identifier) | Q(username=identifier)).first()

#         if not user_obj:
#             messages.error(request, 'Invalid Phone Number, Username, or Password!')
#             return redirect('login')  # Ensure 'login' exists in your urls.py

#         # Authenticate user
#         user = authenticate(request, username=user_obj.username, password=password)

#         if user is not None:
#             login(request, user)

#             # Superuser Redirect
#             if user.is_superuser:
#                 return redirect('dashboard')  

#             # Staff User Redirect
#             elif user.groups.filter(name='staff').exists():
#                 staff_profile = StaffProfile.objects.filter(staff_field=user).first()
#                 if staff_profile and staff_profile.role:
#                     role_name = staff_profile.role.name.lower()
#                     role_dashboard_map = {
#                         "hr": "hr_dashboard",
#                         "teacher": "teacher_dashboard",
#                         "manager": "manager_dashboard",
#                         "accountant": "accountant_dashboard",
#                     }
#                     return redirect(role_dashboard_map.get(role_name, "dashboard")) 

#                 return redirect("dashboard")

#             # Student & Parent Redirects
#             elif user.groups.filter(name='student').exists():
#                 return redirect('student_dashboard')
#             elif user.groups.filter(name='parent').exists():
#                 return redirect('parent_dashboard')

#             return redirect('dashboard')  

#         else:
#             messages.error(request, 'Invalid credentials!')
#             return redirect('login')

#     return render(request, 'login.html', {'heading': 'Login'})


def auth_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            nxt = request.GET.get("next", None)
            if nxt is None:
                return redirect('dashboard')
            else:
                return redirect(nxt)
        else:
            
            messages.error(request, 'Invalid Username or Password!') 
            return redirect('login')
   
    context={
        'heading': 'Login'
    }
    return render(request,'login.html',context)

@login_required(login_url='login')
def logoutPage(request):
    """
    Logs out the current user and redirects to the login page.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')



@login_required(login_url='login')
def change_password(request):
    """
    Allows the user to change their password. Ensures both new passwords match.
    """
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')

        # Update the user's password
        request.user.password = make_password(new_password)
        request.user.save()

        # Update session to avoid logging out
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password has been successfully updated.')
        return redirect('dashboard')

    context = {
        'heading': 'Change Password',
        'subheading': 'Update your account password'
    }
    return render(request, 'change_password.html', context)

# -----------------------------------------------Addmission Session Views-----------------------------------------


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_addmission_session(request):
    listsession = Admission_Year.objects.all()
    context = {
        'listsession': listsession
    }
    return render(request, 'core/session/list_admission_session.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_addmission_session(request, pk):
    sessionname = get_object_or_404(Admission_Year, pk=pk)
    if request.method == 'POST':
        form = Yearform(request.POST, instance=sessionname)
        if form.is_valid:
            form.save()
            messages.success(request, 'Session Year has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                            "messages": 'Success',
                            "sessionListChanged": "sessionListChanged"
                        })})
    else:
        form = Yearform(instance=sessionname)

    context = {
        'form': form
    }

    return render(request, 'core/session/add_admission_session.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_addmission_session(request, pk):
    sessionname = get_object_or_404(Admission_Year, pk=pk)
    sessionname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'sessionListChanged'})

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))

def set_academic_year(request):
    if request.method == 'POST':
        academic_year = request.POST.get('academic_year')
        admission_year_instance = get_object_or_404(Admission_Year, name=academic_year)
        obj = Admission_Year.objects.get(pk=admission_year_instance.id)
        obj.name = academic_year
        obj.save()
        data = {'success': True, 'message': 'Data updated successfully'}


        return JsonResponse(data)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
# -----------------------------------------------Class Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_classname(request):
    stuclass = StudentClass.objects.all()
    context = {
        'stuclass': stuclass
    }
    return render(request, 'core/classname/listclass.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_classname(request, pk):
    
    classname = get_object_or_404(StudentClass, pk=pk)
    if request.method == 'POST':
        form = Classform(request.POST, instance=classname)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session Year has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                            "messages": 'Success',
                            "classListChanged": "classListChanged"
                        })})
    else:
        form = Classform(instance=classname)

    context = {
        'form': form
    }

    return render(request, 'core/classname/addclass.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_classname(request, pk):
    classname = get_object_or_404(StudentClass, pk=pk)

    classname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'classListChanged'})


# -----------------------------------------------Section Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_sectionname(request):
    listsection = StudentSection.objects.all()
    context = {
        'listsection': listsection,
    }
    return render(request, 'core/section/listsection.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_sectionname(request, pk):
    sectionname = get_object_or_404(StudentSection, pk=pk)
    if request.method == 'POST':
        form = Sectionform(request.POST, instance=sectionname)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section Name has been Updates ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                        "messages": 'Success',
                        "sectionListChanged": "sectionListChanged"
                    })})
    else:
        form = Sectionform(instance=sectionname)

    context = {
        'form': form
    }

    return render(request, 'core/section/addsection.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_sectionname(request, pk):
    sectionname = get_object_or_404(StudentSection, pk=pk)
    sectionname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'sectionListChanged'})


# -----------------------------------------------Group Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_groupname(request):
    listgroup = StuGroup.objects.all()
    context = {
        'listgroup': listgroup,
    }
    return render(request, 'core/group/listgroup.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_groupname(request, pk):
    groupname = get_object_or_404(StuGroup, pk=pk)
    if request.method == 'POST':
        form = Groupform(request.POST, instance=groupname)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group Name has been Updates ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                        "messages": 'Success',
                        "groupListChanged": "groupListChanged"
                    })})
    else:
        form = Groupform(instance=groupname)

    context = {
        'form': form
    }

    return render(request, 'core/group/addgroup.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_groupname(request, pk):
    groupname = get_object_or_404(StuGroup, pk=pk)
    groupname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'groupListChanged'})


# -----------------------------------------------Subject Views-----------------------------------------
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_subjectname(request):
    sub = Subject.objects.all()
    context = {
        'sub': sub
    }
    return render(request, 'core/subject/listsubject.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_subjectname(request, pk):
    subjectname = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = Subjectform(request.POST, instance=subjectname)
        if form.is_valid:
            form.save()
            messages.success(request, 'Subject Name has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                            "messages": 'Success',
                            "subjectListChanged": "subjectListChanged"
                        })})
    else:
        form = Subjectform(instance=subjectname)

    context = {
        'form': form
    }

    return render(request, 'core/subject/addsubject.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_subjectname(request, pk):
    subjectname = get_object_or_404(Subject, pk=pk)
    subjectname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'subjectListChanged'})




# -----------------------------------------------Shift Views-----------------------------------------


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_shiftname(request):
    listshift = StudentShift.objects.all()
    context = {
        'listshift': listshift
    }
    return render(request, 'core/shift/listshift.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_shift(request, pk):
    shiftname = get_object_or_404(StudentShift, pk=pk)
    if request.method == 'POST':
        form = Shiftform(request.POST, instance=shiftname)
        if form.is_valid:
            form.save()
            messages.success(request, 'Shift Name has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                            "messages": 'Success',
                            "shiftListChanged": "shiftListChanged"
                        })})
    else:
        form = Shiftform(instance=shiftname)

    context = {
        'form': form
    }

    return render(request, 'core/shift/addshift.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_shift(request, pk):
    shiftname = get_object_or_404(StudentShift, pk=pk)
    shiftname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'shiftListChanged'})



# -----------------------------------------------Period Views-----------------------------------------


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_periodname(request):
    listperiod = Period.objects.all()
    context = {
        'listperiod': listperiod
    }
    return render(request, 'core/period/listperiod.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_periodname(request, pk):
    periodname = get_object_or_404(Period, pk=pk)
    if request.method == 'POST':
        form = Periodform(request.POST, instance=periodname)
        if form.is_valid:
            form.save()
            messages.success(request, 'Group Name has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                            "messages": 'Success',
                            "periodListChanged": "periodListChanged"
                        })})
    else:
        form = Periodform(instance=periodname)

    context = {
        'form': form
    }

    return render(request, 'core/period/addperiod.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_periodname(request, pk):
    periodname = get_object_or_404(Period, pk=pk)
    periodname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'periodListChanged'})

# -----------------------------------------------Role Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_roletype(request):
    list_role_type = RoleType.objects.all()
    context = {
        'list_role_type': list_role_type
    }
    return render(request, 'core/role/list_role.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_roletype(request, pk):
    role_type = get_object_or_404(RoleType, pk=pk)
    if request.method == 'POST':
        form = RoleTypeForm(request.POST, instance=role_type)
        if form.is_valid:
            form.save()
            messages.success(request, 'Role Type has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                            "messages": 'Success',
                            "periodListChanged": "roleListChanged"
                        })})
    else:
        form = RoleTypeForm(instance=role_type)

    context = {
        'form': form
    }

    return render(request, 'core/role/add_role.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_roletype(request, pk):
    role_type = get_object_or_404(RoleType, pk=pk)
    role_type.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'roleListChanged'})


# -----------------------------------------------Chossable Subject-----------------------------------------
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def choosable_subject(request):
    classList = ClassConfig.objects.filter(class_group_id__group_id__isnull=False)
    sessionList = AcademicSession.objects.all()
    studentlist, subject_list, student_subjects_data,class_instance = None, None, [],None

    if request.method == 'POST':

        if 'modal_compulsory' in request.POST and 'modal_optional' in request.POST:
            # Handle modal submission
            selected_students_modal = request.POST.get('selected_students_modal')
            modal_compulsory = request.POST.get('modal_compulsory')
            modal_optional = request.POST.get('modal_optional')

            if selected_students_modal:
                selected_student_ids = selected_students_modal.split(',')

                for student_id in selected_student_ids:
                    student_instance = get_object_or_404(StudentProfile, pk=student_id)

                    # Update compulsory subject
                    if modal_compulsory:
                        compulsory_subject = get_object_or_404(SubjectConfig, pk=modal_compulsory)
                        Forth_Sub.objects.update_or_create(
                            student_id=student_instance,
                            forth_type="COMPULSARY",
                            defaults={"sub_conf_id": compulsory_subject}
                        )

                    # Update optional subject
                    if modal_optional:
                        optional_subject = get_object_or_404(SubjectConfig, pk=modal_optional)
                        Forth_Sub.objects.update_or_create(
                            student_id=student_instance,
                            forth_type="OPTIONAL",
                            defaults={"sub_conf_id": optional_subject}
                        )

                messages.success(request, 'Subjects have been assigned successfully via modal!')
            return redirect('choosable_subject')
        
        class_id =request.POST.get("class_id")
        session_id =request.POST.get("session_id")
        if class_id:
            class_instance= get_object_or_404(ClassConfig, pk=class_id)
            session_instance= get_object_or_404(AcademicSession, pk=session_id)
            studentlist = StudentProfile.objects.filter(Q(class_id=class_instance) & Q(academic_session_year=session_instance) & Q(student_field__status="Active")).order_by("roll_no")
            subject_list=SubjectConfig.objects.filter(Q(class_id=class_instance.class_group_id) & Q(subject_type="CHOOSABLE") )
            
            forth_subs = Forth_Sub.objects.filter(student_id__in=studentlist)

            for student in studentlist:
                student_subjects_data.append({
                    "student": student,
                    "COMPULSARY": [
                        sub.sub_conf_id.subject_id.name for sub in forth_subs
                        if sub.student_id == student and sub.forth_type == "COMPULSARY"
                    ],
                    "OPTIONAL": [
                        sub.sub_conf_id.subject_id.name for sub in forth_subs
                        if sub.student_id == student and sub.forth_type == "OPTIONAL"
                    ],
                })
            
        
    context={
        'classList':classList,
        'sessionList':sessionList,
        'studentlist':studentlist,
        'subject_list':subject_list,
        'student_subjects_data': student_subjects_data,
        'class_instance':class_instance,
        'heading':'Student',
        'subheading':'choosable_subject',
        }
    
    return render(request, 'core/choosable_subject/choosable_subject.html', context) 

def get_choosable_subject(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)

    # Fetch existing subjects for the student
    compulsory_subject = Forth_Sub.objects.filter(student_id=student, forth_type="COMPULSARY").first()
    optional_subject = Forth_Sub.objects.filter(student_id=student, forth_type="OPTIONAL").first()

    return JsonResponse({
        'compulsory_subject': compulsory_subject.sub_conf_id.id if compulsory_subject else None,
        'optional_subject': optional_subject.sub_conf_id.id if optional_subject else None,
    })


# -----------------------------------------------Mark Type Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_marktype(request):
    listmarktype = Mark_type.objects.all()
    context = {
        'listmarktype': listmarktype,
    }
    return render(request, 'core/mark/list_mark_type.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_marktype(request, pk):
    marktypename = get_object_or_404(Mark_type, pk=pk)
    if request.method == 'POST':
        form = MarkTypeform(request.POST, instance=marktypename)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section Name has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                        "messages": 'Success',
                        "markTypeChanged": "markTypeChanged"
                    })})
    else:
        form = MarkTypeform(instance=marktypename)

    context = {
        'form': form
    }

    return render(request, 'core/mark/add_mark_type.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_marktype(request, pk):
    marktypename = get_object_or_404(Mark_type, pk=pk)
    marktypename.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'markTypeChanged'})



# basic Crud Setup

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def crud_basic(request):
    
    context={
        'heading':'Settings',
        'subheading':'Academic Setup',
    }

    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        name = request.POST.get('name')

        if model_name == 'student_class':
            name = name.strip().title()
            existing_class = StudentClass.objects.filter(name__iexact=name).first()
            if existing_class:
                messages.error(request, 'Class with this name already exists!')
            else:
                StudentClass.objects.create(name=name)
                messages.success(request, 'Class Name has been saved ! ! !')

        elif model_name == 'student_section':
            name = name.strip().title()
            existing_section = StudentSection.objects.filter(name__iexact=name).first()
            if existing_section:
                messages.error(request, 'Section with this name already exists!')
            else:
                StudentSection.objects.create(name=name)
                messages.success(request, 'Section Name has been saved ! ! !')

        elif model_name == 'student_group':
            name = name.strip().title()
            existing_group = StuGroup.objects.filter(name__iexact=name).first()
            if existing_group:
                messages.error(request, 'Group with this name already exists!')
            else:
                StuGroup.objects.create(name=name)
                messages.success(request, 'Group Name has been saved ! ! !')

        elif model_name == 'subject':
            name = name.strip().title()
            existing_subject = Subject.objects.filter(name__iexact=name).first()
            if existing_subject:
                messages.error(request, 'Subject with this name already exists!')
            else:
                Subject.objects.create(name=name)
                messages.success(request, 'Subject Name has been saved ! ! !')

        elif model_name == 'student_shift':
            name = name.strip().title()
            existing_shift = StudentShift.objects.filter(name__iexact=name).first()
            if existing_shift:
                messages.error(request, 'Shift with this name already exists!')
            else:
                StudentShift.objects.create(name=name)
                messages.success(request, 'Shift Name has been saved ! ! !')

        elif model_name == 'class_period':
            name = name.strip()

            if name[0].isdigit():
                name = name.split(' ', 1)
                name[0] = name[0].lower()
                name = ' '.join(name)
            else:
                name = name.title()
            existing_period = Period.objects.filter(name__iexact=name).first()
            if existing_period:
                messages.error(request, 'Period with this name already exists!')
            else:
                Period.objects.create(name=name)
                messages.success(request, 'Period Name has been saved ! ! !')

        elif model_name == 'marktype':
            name = name.strip().title()
            existing_marktype = Mark_type.objects.filter(name__iexact=name).first()
            if existing_marktype:
                messages.error(request, 'Mark Type with this name already exists!')
            else:
                Mark_type.objects.create(name=name)
                messages.success(request, 'Mark Type Name has been saved ! ! !')

        
        elif model_name == 'role':
            name = name.strip().title()
            existing_role = RoleType.objects.filter(name__iexact=name).first()
            if existing_role:
                messages.error(request, 'Role type with this name already exists!')
            else:
                RoleType.objects.create(name=name)
                messages.success(request, 'Role type has been saved ! ! !')


        elif model_name == 'session':
            existing_session = Admission_Year.objects.filter(name=name).first()
            if existing_session:
                messages.error(request, 'Admission Year with this name already exists!')
            else:
                Admission_Year.objects.create(name=name)
                messages.success(request, 'Session Year has been saved ! ! !')

        else:
            messages.danger(request, 'Data Invalid ! ! !')
            return JsonResponse({'message': 'Invalid model_name'})
            

        # Return a JSON response indicating success
        return redirect('basic_setup') 

    return render(request, 'core/basic_setup.html',context)


# -----------------------------------------------Class Config Views-----------------------------------------

def get_class_group_config(request, pk):
    class_group = get_object_or_404(ClassGroupConfig, pk=pk)
    return JsonResponse({
        'id': class_group.id,
        'class_id': class_group.class_id.id,
        'group_id': class_group.group_id.id if class_group.group_id else None,
    })

def get_class_config(request, pk):
    class_config = get_object_or_404(ClassConfig, pk=pk)
    print({
        'id': class_config.id,
        'class_group_id': class_config.class_group_id.id,
        'section_id': class_config.section_id.id if class_config.section_id else None,
        'shift_id': class_config.shift_id.id if class_config.shift_id else None,
    })  # Log the data being returned
    return JsonResponse({
        'id': class_config.id,
        'class_group_id': class_config.class_group_id.id,
        'section_id': class_config.section_id.id if class_config.section_id else None,
        'shift_id': class_config.shift_id.id if class_config.shift_id else None,
    })


@csrf_exempt
def update_class_group_config(request, pk):
    if request.method == "POST":
        class_group = get_object_or_404(ClassGroupConfig, pk=pk)
        class_id = request.POST.get('class_id')
        group_id = request.POST.get('group_id')
        class_group.class_id = get_object_or_404(StudentClass, pk=class_id)
        if group_id and group_id.strip():  # Check if group_id is not empty or just whitespace
            class_group.group_id = StuGroup.objects.filter(pk=group_id).first()
        else:
            class_group.group_id = None
        class_group.save()
        return JsonResponse({'success': True})

@csrf_exempt    
def delete_class_group_config(request, pk):
    if request.method == "POST":
        class_group_config = get_object_or_404(ClassGroupConfig, pk=pk)
        class_group_config.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def update_class_config(request, pk):
    if request.method == "POST":
        print(pk)
        class_config = get_object_or_404(ClassConfig, pk=pk)
        class_group_id = request.POST.get('class_group_id')
        section_id = request.POST.get('section_id')
        shift_id = request.POST.get('shift_id')
        print(class_group_id,section_id,shift_id)
        class_config.class_group_id = get_object_or_404(ClassGroupConfig, pk=class_group_id)
        if section_id and section_id.strip():  # Check if group_id is not empty or just whitespace
            class_config.section_id = StudentSection.objects.filter(pk=section_id).first()
        else:
            class_config.section_id = None

        if shift_id and shift_id.strip():  # Check if group_id is not empty or just whitespace
            class_config.shift_id = StudentShift.objects.filter(pk=shift_id).first()
        else:
            class_config.shift_id = None
        
        class_config.save()
        return JsonResponse({'success': True})

@csrf_exempt
def delete_class_config(request, pk):
    if request.method == "POST":
        class_config = get_object_or_404(ClassConfig, pk=pk)
        class_config.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_class_config(request):
    
    class_list= StudentClass.objects.all()
    group_list= StuGroup.objects.all()
    shift_list= StudentShift.objects.all()
    class_group_list = ClassGroupConfig.objects.all().order_by('class_id')
    class_section_list = StudentSection.objects.all()
    class_config_list = ClassConfig.objects.all()

    if request.method == 'POST':
        if 'class_id' in request.POST or 'group_id' in request.POST:
            class_id = request.POST.get('class_id')
            class_instance = get_object_or_404 (StudentClass, pk=class_id)
            group_id_list = request.POST.getlist('group_id')
            created = False
            if group_id_list:
                for group_id in group_id_list:
                    group_instance = get_object_or_404 (StuGroup, pk=group_id)
                    classGroup = ClassGroupConfig(class_id=class_instance,group_id=group_instance)
                    existing_classGroupConfig = ClassGroupConfig.objects.filter(Q(class_id=class_id) & Q(group_id=group_id)).first()

                    if not existing_classGroupConfig:
                        classGroup.save()
                        created = True
                        
                    
                    else:
                        messages.error(request, 'Group Config with the same name already exist ! ! !')
                        break
            
            else:
                existing_classGroupConfig = ClassGroupConfig.objects.filter(Q(class_id=class_id)).first()
                if existing_classGroupConfig:
                    messages.error(request, 'Group Config with the same name already exist ! ! !')
                    return redirect('list_class_config')
                else:
                    classGroup = ClassGroupConfig(class_id=class_instance)
                    classGroup.save()
                    created = True

                if created:
                    messages.success(request, 'Group Config has been created')
                    return redirect('list_class_config')
        
        elif 'class_group_id' in request.POST:
            class_group_id = request.POST.get('class_group_id')
            section_id_list = request.POST.getlist('section_id')  
            shift_id = request.POST.get('shift_id')

            class_group_instance = get_object_or_404(ClassGroupConfig, pk=class_group_id)
            shift_instance = StudentShift.objects.filter(pk=shift_id).first()
            created = False

            if section_id_list and shift_id:
                for section_id in section_id_list:
                    section_instance = StudentSection.objects.filter(pk=section_id).first()

                    # Check for duplicate configurations
                    existing_classConfig = ClassConfig.objects.filter(
                        class_group_id=class_group_instance,
                        section_id=section_instance,
                        shift_id=shift_instance
                    ).first()

                    if not existing_classConfig:
                        # Create new ClassConfig
                        class_config = ClassConfig(
                            class_group_id=class_group_instance,
                            section_id=section_instance,
                            shift_id=shift_instance
                        )
                        class_config.save()
                        created = True
                    else:
                        messages.error(request, f'Class Config for section {section_instance} already exists!')
                        break
            elif section_id_list:
                # Process configurations for each selected section
                for section_id in section_id_list:
                    section_instance = StudentSection.objects.filter(pk=section_id).first()

                    existing_classConfig = ClassConfig.objects.filter(
                        class_group_id=class_group_instance,
                        section_id=section_instance,
                        shift_id=None  # Can be None
                    ).first()

                    if not existing_classConfig:
                        # Create a new configuration for each section
                        class_config = ClassConfig(
                            class_group_id=class_group_instance,
                            section_id=section_instance,
                            shift_id=shift_id  # Can be None
                        )
                        class_config.save()
                        created = True
                    else:
                        messages.error(request, f'Class Config for section {section_instance} with shift {shift_id} already exists!')
            elif shift_id:
                # If no sections are selected, create a configuration with only the shift
                existing_classConfig = ClassConfig.objects.filter(
                    class_group_id=class_group_instance,
                    section_id=None,
                    shift_id=shift_id
                ).first()

                if not existing_classConfig:
                    class_config = ClassConfig(
                        class_group_id=class_group_instance,
                        section_id=None,
                        shift_id=shift_id
                    )
                    class_config.save()
                    created = True
                else:
                    messages.error(request, f'Class Config with shift {shift_id} already exists!')
            else:
                # If both section_id_list and shift_id are empty, create a configuration without them
                existing_classConfig = ClassConfig.objects.filter(
                    class_group_id=class_group_instance,
                    section_id=None,
                    shift_id=None
                ).first()

                if not existing_classConfig:
                    class_config = ClassConfig(
                        class_group_id=class_group_instance,
                        section_id=None,
                        shift_id=None
                    )
                    class_config.save()
                    created = True
                else:
                    messages.error(request, 'Class Config with no section or shift already exists!')

            if created:
                messages.success(request, 'Class Config(s) have been created.')
            return redirect('list_class_config')
            
    context={
        'class_list':class_list,
        'group_list':group_list,
        'shift_list':shift_list,
        'class_group_list':class_group_list,
        'class_section_list':class_section_list,
        'class_config_list':class_config_list,
        'heading':'Settings',
        'subheading':'Class Config',
    }
    return render(request,'core/classconfig/list_class_config.html',context) 




# -----------------------------------------------Period Config Views-----------------------------------------
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_in_group(user))
def period_config(request):
    classes = ClassConfig.objects.all()
    periods = Period.objects.all()

    if request.method == 'POST':
        try:
            # Use a transaction to ensure atomicity
            with transaction.atomic():
                for class_obj in classes:
                    for period in periods:
                        # Retrieve start and end time for each class and period combination
                        start_time_key = f'start_time_{class_obj.id}_{period.id}'
                        end_time_key = f'end_time_{class_obj.id}_{period.id}'
                        break_time_key = f'break_time_{class_obj.id}_{period.id}'

                        start_time = request.POST.get(start_time_key)
                        end_time = request.POST.get(end_time_key)
                        break_time = request.POST.get(break_time_key) == 'on'
                        
                         # Skip if both start and end times are empty
                        if not start_time or not end_time:
                            continue

                        # Either update an existing record or create a new one
                        PeriodConfig.objects.update_or_create(
                            class_id=class_obj,
                            period_id=period,
                            defaults={
                                'start_time': start_time,
                                'end_time': end_time,
                                'break_time': break_time,
                            }
                        )
            # Redirect to the same page after saving
            return redirect('class_routine_view') 
        except Exception as e:
            print(f"Error: {e}")
            # Handle errors or display an error message if needed

    # Fetch existing period configurations for rendering
    period_configs = PeriodConfig.objects.select_related('class_id', 'period_id').all()
    grouped_configs = {}
    for config in period_configs:
        class_name = config.class_id.class_group_id.class_id.name
        if class_name not in grouped_configs: 
            grouped_configs[class_name] = {}
        grouped_configs[class_name][config.period_id.name] = {
            'start_time': config.start_time,
            'end_time': config.end_time,
            'break_time': config.break_time,
        }
    context={
        'classes': classes,
        'periods': periods,
        'grouped_configs': grouped_configs, 
        'heading':'Settings',
        'subheading':'Period Config',
    }
    return render(request,'core/periodconfig/period_config.html',context)


# -----------------------------------------------Subject Assign Views-----------------------------------------


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def create_subject_assign(request):
    subjectlist = Subject.objects.all()
    classlist = ClassGroupConfig.objects.all()
    
    if request.method == 'POST': 
        class_id = request.POST.get('class_id')
        if class_id:
            class_instance = get_object_or_404(ClassGroupConfig, pk=class_id)
        
        if class_id:
            existing_class = SubjectAssign.objects.filter(Q(class_id=class_instance)).exists()
            if existing_class:
                existing_subject_assign = SubjectAssign.objects.filter(class_id=class_id).first()
                form = SubjectAssignForm(request.POST, instance=existing_subject_assign)
            else:
                form = SubjectAssignForm(request.POST)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Subject Assign has been Saved/Updated!')
                return redirect('create_subject_assign')  
        
    context = {
        'subjectlist': subjectlist,
        'classlist': classlist,
        'heading': 'Settings',
        'subheading': 'Subject Assign'
    }
    return render(request, 'core/subject/subject_assign.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def create_teacher_assign(request):
    teacherlist= StaffProfile.objects.filter(Q(staff_field__status="Active") & Q(role__name="Teacher"))
    print(teacherlist)
    subjectlist = Subject.objects.all()
    classlist = ClassConfig.objects.all() 
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        subjects = request.POST.getlist('subjects')
        classes = request.POST.getlist('classes')

        # Get or create the TeacherSubjectAssign instance
        teacher_subject_assign, created = TeacherSubjectAssign.objects.get_or_create(
            teacher_id=teacher_id,
            defaults={'teacher_id': StaffProfile.objects.get(id=teacher_id)}
        )

        # Update the subjects and classes assignments
        teacher_subject_assign.subject_assigns.set(subjects)
        teacher_subject_assign.class_assigns.set(classes)
        teacher_subject_assign.save()
        messages.success(request, 'Teacher Assign has been Saved/Updated!')
        return redirect('create_teacher_assign')  
        
    context = {
        'teacherlist':teacherlist,
        'subjectlist': subjectlist,
        'classlist': classlist,
        'heading': 'Settings',
        'subheading': 'Teacher Subject Assign'
    }
    return render(request, 'core/subject/subject_assign_teacher.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
@csrf_exempt 
def get_subject_assign(request, class_id):
    subject_assign = SubjectAssign.objects.filter(class_id=class_id)
    subject_list = list(subject_assign.values('subjects'))
    return JsonResponse(subject_list, safe=False)
 
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
@csrf_exempt 
def get_teacher_assign(request, teacher_id):
    if request.method == 'GET':
        try:
            teacher_subject_assign = TeacherSubjectAssign.objects.get(teacher_id=teacher_id)
            subject_assigns = list(teacher_subject_assign.subject_assigns.values_list('id', flat=True))
            class_assigns = list(teacher_subject_assign.class_assigns.values_list('id', flat=True))
        except TeacherSubjectAssign.DoesNotExist:
            subject_assigns = []
            class_assigns = []
        data = {
            'subjects': subject_assigns,
            'classes': class_assigns
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# -----------------------------------------------Subject Config Views-----------------------------------------
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_subject_conf(request):
    classlist = ClassGroupConfig.objects.all()

    context = { 
        'heading': 'Settings',
        'subheading': 'List Class Mark Config',
        'classlist': classlist
    }
    return render(request, 'core/subjectconfig/list_subject_conf.html', context)




@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def create_subject_conf(request,studentclass):
    class_instance = get_object_or_404(ClassGroupConfig, pk=studentclass)
    try:
        subject_assign = SubjectAssign.objects.get(class_id=class_instance.id)
        subjects_queryset = subject_assign.subjects.all()
    except SubjectAssign.DoesNotExist:
        subjects_queryset = Subject.objects.none()  
        messages.error(request, 'No SubjectAssign found for this class group.')
    
    SubjectFormSet = inlineformset_factory(
            parent_model=ClassGroupConfig,
            model=SubjectConfig, 
            form=SubjectConfigForm,
            extra=5,
            can_delete=True,
        )
    if request.method == 'POST':
            formset = SubjectFormSet(request.POST, instance=class_instance)
            
            if formset.is_valid():
                for form in formset.forms:
                    if form.cleaned_data.get('subject_id'):  # Check if subject_id is provided
                        form.save()  # Save only valid forms
                    elif not form.cleaned_data.get('DELETE'):
                        # Skip forms without a subject_id and not marked for deletion
                        form.add_error('subject_id', ValidationError("Subject is required."))
                messages.success(request, 'Subject Config has been saved!')
                return redirect(request.META.get('HTTP_REFERER', 'list_subject_conf'))
            
    else:
        
        formset = SubjectFormSet(instance=class_instance)
        for form in formset.forms:
            form.fields['subject_id'].queryset = subjects_queryset

    context = {
        'heading': 'Settings',
        'subheading': 'Subject Mark Config',
        'formset': formset,
        'class_instance': class_instance
    }

    return render(request, 'core/subjectconfig/create_subject_conf.html', context)

    
    
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_subject_conf(request, pk):
    subject_conf = get_object_or_404(SubjectConfig, pk=pk)
    subject_conf.delete()
    return redirect(request.META['HTTP_REFERER'])


# -----------------------------------------------Mark Config Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_mark_config(request):
    classlist = ClassGroupConfig.objects.all()
    context = { 
        'heading': 'Settings', 
        'subheading': 'List Mark Config',
        'classlist': classlist
    }
    return render(request, 'core/mark/list_mark_conf.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))

def create_mark_conf(request, studentclass):
    class_instance = get_object_or_404(ClassGroupConfig, pk=studentclass)
    
    subject_configs = SubjectConfig.objects.filter(class_id=class_instance)
    mark_type_configs= Mark_type.objects.all()

    MarkFormSet = inlineformset_factory(
        parent_model=ClassGroupConfig,
        model=Mark_config,
        form=Markconfigform, 
        extra=5,
        can_delete=True,
    )

    if request.method == 'POST':
        formset = MarkFormSet(request.POST, instance=class_instance)
        
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Mark Config has been saved!')
            return redirect(request.META.get('HTTP_REFERER'))
       
    else:
        formset = MarkFormSet(instance=class_instance)
        for form in formset:
            form.fields['subject_conf_id'].queryset = subject_configs
            form.fields['mark_type_id'].queryset = mark_type_configs
            # form.fields['academic_year'].initial = admission_year

    context = {
        'heading': 'Settings',
        'subheading': 'Mark Config',
        'formset': formset,
        'class_instance': class_instance,
    }

    return render(request, 'core/mark/create_mark_conf.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_mark_conf(request, pk):
    mark_config = get_object_or_404(Mark_config, pk=pk)
    mark_config.delete()
    return redirect(request.META['HTTP_REFERER']) 



def submit_mark_config(request):
    subject_types = SubjectConfig.SUBJECT_TYPE
    all_subjects = Subject.objects.all()
    all_classes = ClassGroupConfig.objects.all()
    mark_types = Mark_type.objects.all()

    all_subject_count = all_subjects.count()  # Total number of subjects

    # Create a mapping of class_id to assigned subjects
    class_subjects_map = {}
    class_empty_slots = {}  # Store empty slots per class

    for class_group in all_classes:
        assigned_subjects = list(Subject.objects.filter(
            id__in=SubjectAssign.objects.filter(class_id=class_group).values_list('subjects', flat=True)
        ))
        class_subjects_map[class_group.id] = assigned_subjects

        # Compute empty slots per class
        empty_slots = max(0, all_subject_count - len(assigned_subjects))
        class_empty_slots[class_group.id] = range(empty_slots)  # Store a range for iteration in the template

    if request.method == 'POST':
        try:
            subject_config_data = json.loads(request.POST.get('subject_config_data', '[]'))
            with transaction.atomic():
                for entry in subject_config_data:
                    class_id = entry.get('class_id')
                    subject_id = entry.get('subject_id')
                    subject_serial = entry.get('subject_Serial')
                    subject_merge = entry.get('subject_marge')
                    subject_type = entry.get('subject_type')
                    subject_mark = entry.get('mark')

                    subject_conf, created = SubjectConfig.objects.update_or_create(
                        class_id=ClassGroupConfig.objects.get(id=class_id),
                        subject_id=Subject.objects.get(id=subject_id),
                        defaults={
                            'subject_Serial': int(float(subject_serial or 0)),
                            'subject_type': subject_type,
                            'mark': int(float(subject_mark or 0)),
                            'subject_marge': int(float(subject_merge or 0))
                        }
                    )

                    mark_configs_data = entry.get('markConfigData')
                    for item in mark_configs_data:
                        mark_type_id = item.get('mark_type_id')
                        mark_type_mark = item.get('mark')
                        mark_type_pass_mark = item.get('pass_mark')

                        Mark_config.objects.update_or_create(
                            class_id=ClassGroupConfig.objects.get(id=class_id),
                            subject_conf_id=SubjectConfig.objects.get(id=subject_conf.id),
                            mark_type_id=Mark_type.objects.get(id=mark_type_id),
                            defaults={
                                'mark': int(float(mark_type_mark or 0)),
                                'pass_mark': int(float(mark_type_pass_mark or 0))
                            }
                        )

            return redirect('submit_mark_config') 
        except Exception as e:
            print(f"Error: {e}")

    subject_confs = SubjectConfig.objects.all().select_related('subject_id', 'class_id')
    mark_confs = Mark_config.objects.all().select_related('class_id', 'subject_conf_id', 'mark_type_id')

    subject_configs = {}
    mark_configs = {}

    for item in subject_confs:
        class_name = item.class_id
        subject = item.subject_id.name
        if class_name not in subject_configs:
            subject_configs[class_name] = {}
        subject_configs[class_name][subject] = {
            'subject_conf_id': item.id,
            'subject_type': item.subject_type,
            'subject_mark': item.mark,
            'subject_serial': item.subject_Serial,
            'subject_merge': item.subject_marge
        }

    for item in mark_confs:
        class_name = item.class_id
        subject_conf_id = item.subject_conf_id.id
        mark_type_id = item.mark_type_id.id
        if class_name not in mark_configs:
            mark_configs[class_name] = {}
        if subject_conf_id not in mark_configs[class_name]:
            mark_configs[class_name][subject_conf_id] = {}
        mark_configs[class_name][subject_conf_id][mark_type_id] = {
            'mark_type_mark': item.mark,
            'mark_type_pass_mark': item.pass_mark
        }

    context = {
        'subject_types': subject_types,
        'all_subjects': all_subjects,
        'class_subjects_map': class_subjects_map,
        'all_classes': all_classes,
        'mark_types': mark_types,
        'subjectConfigs': subject_configs, 
        'markConfigs': mark_configs,
        'all_subject_count': all_subject_count,
        'class_empty_slots': class_empty_slots, 
        'heading': 'Settings',
        'subheading': 'Mark Config',
    }

    return render(request, 'core/mark/submit_mark_config.html', context)



@login_required(login_url='login')
def check_class_group(request, class_id):
    has_group_check = ClassGroupConfig.objects.filter(id=class_id, group_id__isnull=False)
    print(has_group_check)
    has_group = ClassGroupConfig.objects.filter(id=class_id, group_id__isnull=False).exists()
    return JsonResponse({'has_group': has_group})






 
