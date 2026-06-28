from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse,HttpResponseBadRequest
from .forms import *
from .models import *
from django.contrib import messages
import json
from django.db.models import Q
from user.decorators import *
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse
from miscellaneous.models import Institute
from django.forms import inlineformset_factory
from core.models import ClassConfig,SubjectConfig,Mark_type,ClassGroupConfig,StudentClass,StudentShift,StudentSection
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db.models import Sum
import math
import time
from sms.utils import *
from crucial.models import SMSUsage, SMS, SMSLimit, SMSTemplateNotification,Routine
from datetime import datetime
from django.templatetags.static import static
# -------------------------------------ExamName ----------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def examname(request):
    context = {
        'heading': 'Exam',
        'subheading': 'Exam Name',
    }
    return render(request, 'exams/examname/examname.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_examname(request):
    # Show exam names from ALL years, ordered by newest first
    examname = Examname.objects.all().order_by('-academic_year__name', 'name')
    context = {
        'examname': examname
    }
    return render(request, 'exams/examname/listexam.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_examname(request): 
    current_year = str(datetime.now().year)
    admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
    form = Examnameform(initial={'academic_year': admission_year})
    if request.method == 'POST':
        form = Examnameform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam Name has been saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "examListChanged": "examListChanged"
                })})
    

    context = {
        'form': form
    }

    return render(request, 'exams/examname/addexam.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_examname(request, pk):
    examname = get_object_or_404(Examname, pk=pk)
    if request.method == 'POST':
        form = Examnameform(request.POST, instance=examname)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam Name has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "examListChanged": "examListChanged"
                })})
    else:
        form = Examnameform(instance=examname)

    context = {
        'form': form
    }

    return render(request, 'exams/examname/addexam.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_examname(request, pk):
    examname = get_object_or_404(Examname, pk=pk)
    examname.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'examListChanged'})


# -----------------------------------------------Syllabus Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def syllabus(request):
    context = {
        'heading': 'Exam',
        'subheading': 'Syllabus',
    }
    return render(request, 'exams/syllabus/syllabus.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_syllabus(request):
    current_year = str(datetime.now().year)
    admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
    syllabuslist = Syllabus.objects.filter(
        academic_year=admission_year
    )
    context = {
        'syllabuslist': syllabuslist
    }
    return render(request, 'exams/syllabus/listsyllabus.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_syllabus(request):
    current_year = str(datetime.now().year)
    admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
    form = SyllabusForm(initial={'academic_year': admission_year})
    form.fields['exam_name'].queryset = Examname.objects.filter(academic_year=admission_year)
    form.fields['classname'].queryset = ClassGroupConfig.objects.all()
    form.fields['subject_id'].queryset = Subject.objects.all()

    if request.method == 'POST':
        form = SyllabusForm(request.POST, request.FILES)
        if form.is_valid():
            
            form.save()
            messages.success(request, 'Syllabus has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "syllabusListChanged": "syllabusListChanged"
                })})

    context = {
        'form': form,
    }

    return render(request, 'exams/syllabus/addsyllabus.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_syllabus(request, pk):
    syllabus = get_object_or_404(Syllabus, pk=pk)
    current_year = str(datetime.now().year)
    admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
    if request.method == 'POST':
        form = SyllabusForm(request.POST, request.FILES, instance=syllabus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Syllabus has been Edited ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "syllabusListChanged": "syllabusListChanged"
                })})
    else:
        form = SyllabusForm(instance=syllabus, initial={'academic_year': admission_year})
        # Filter the exam_name field queryset based on the latest Admission_Year
        form.fields['exam_name'].queryset = Examname.objects.filter(academic_year=admission_year)

    context = {
        'form': form
    }

    return render(request, 'exams/syllabus/addsyllabus.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_syllabus(request, pk):
    syllabus = get_object_or_404(Syllabus, pk=pk)
    syllabus.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'syllabusListChanged'})


# -----------------------------------------------Grade Views-----------------------------------------
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def grade(request):
    context = {
        'heading': 'Exam',
        'subheading': 'Grade',
    }
    return render(request, 'exams/grade/grade.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_grade(request):
    gradelist = Graderule.objects.all()
    context = {
        'gradelist': gradelist
    }
    return render(request, 'exams/grade/listgrade.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_grade(request):
    if request.method == 'POST':
        form = Gradeform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "gradeListChanged": "gradeListChanged"
                })})
    else:
        form = Gradeform()

    context = {
        'form': form
    }

    return render(request, 'exams/grade/addgrade.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_grade(request, pk):
    grade = get_object_or_404(Graderule, pk=pk)
    if request.method == 'POST': 
        form = Gradeform(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade has been Edited ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "gradeListChanged": "gradeListChanged"
                })})
    else:
        form = Gradeform(instance=grade)

    context = {
        'form': form
    }

    return render(request, 'exams/grade/addgrade.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_in_group(user))
def del_grade(request, pk):
    grade = get_object_or_404(Graderule, pk=pk)
    grade.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'gradeListChanged'})


# -----------------------------------------------Schedule Views-----------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_schedule(request):
    schedulelist = ClassConfig.objects.all()
    context = {
        'heading': 'Exam',
        'subheading': 'List Exam Routine',
        'schedulelist': schedulelist,
    }
    return render(request, 'exams/schedule/schedule.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def create_schedule(request, class_name):
    current_year = str(datetime.now().year)
    admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
    class_name_instance = get_object_or_404(ClassConfig, pk=class_name)
    
    try:
        subject_assign = SubjectAssign.objects.get(class_id=class_name_instance.class_group_id)
        subjects_queryset = subject_assign.subjects.all()
    except SubjectAssign.DoesNotExist:
        subjects_queryset = Subject.objects.none()  # Set to an empty queryset
    
    exam_queryset = Examname.objects.all().order_by('-academic_year__name', 'name')
    ScheduleFormSet = inlineformset_factory(
        parent_model=ClassConfig,  
        model=Schedule,
        form=Scheduleform,
        extra=3,  
        can_delete=True,
    )
    
    if request.method == 'POST':
        formset = ScheduleFormSet(request.POST, instance=class_name_instance)
        
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.academic_year = admission_year
                instance.save()
            formset.save_m2m()
            messages.success(request, 'Routine has been Saved ! ! !')
            return redirect(request.META['HTTP_REFERER'])
        
    else:
        formset = ScheduleFormSet(instance=class_name_instance)
        for form in formset.forms:
            form.fields['subject_id'].queryset = subjects_queryset  # Ensure queryset is valid
            form.fields['exam_name'].queryset = exam_queryset

    context = {
        'heading': 'Exam',
        'subheading': 'Exam Routine',
        'formset': formset,
        'class_name_instance': class_name_instance
    }

    return render(request, 'exams/schedule/addschedule.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_schedule(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    schedule.delete()
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"student", "parent","teacher", roles=['Manager','HR']))
def exam_schedule(request):
    
    exam_dates = []
    exam_config = {}
    exams = Schedule.objects.select_related('subject_id', 'class_name', 'exam_name').all().order_by('exam_date')
    class_items = None
    exam_items = None
    if request.method == 'POST':
        class_names = [int(name) for name in request.POST.getlist('class_input')]
        exam_names = [int(name) for name in request.POST.getlist('exam_input')]

        distinct_exam_dates = Schedule.objects.filter(exam_name__in=exam_names, class_name__in=class_names).values('exam_date').distinct().order_by('exam_date')

        for i, date in enumerate(distinct_exam_dates):
            exam_dates.append({
                "index": i+1,
                "weekday": date["exam_date"].strftime("%A"),
                "formatted_date": date["exam_date"].strftime("%d-%m-%y"),
            })

        filters = {}
        if class_names:
            filters['class_name__in'] = class_names
            class_items = ClassConfig.objects.filter(id__in=class_names)
        if exam_names:
            filters['exam_name__in'] = exam_names
            exam_items = Examname.objects.filter(id__in=exam_names)

        exams = Schedule.objects.select_related('subject_id', 'class_name', 'exam_name').filter(**filters).order_by('exam_date')
    
    for exam in exams:
        class_name = exam.class_name
        exam_date = exam.exam_date.strftime("%d-%m-%y")
        if class_name not in exam_config:
            exam_config[class_name] = {}
        if exam_date not in exam_config[class_name]:
            exam_config[class_name][exam_date] = []
        exam_config[class_name][exam_date].append({
            "start_time": exam.start_time.strftime("%I:%M %p"),
            "end_time": exam.end_time.strftime("%I:%M %p"),
            "subject_name": exam.subject_id.name,
            "exam_name": exam.exam_name.name,
        })
        
    context = {
        "exam_dates": exam_dates,
        "exam_config": exam_config,
        "classes": class_items,
        "exams": exam_items,
        "all_classes": ClassConfig.objects.all(),
        "all_exams": Examname.objects.all(),
        'heading': 'Exam',
        'subheading': 'Class Wise Schedule',
    }
    return render(request, 'exams/schedule/exam_schedule.html', context)



def admit_card_without_routine(request):
    classList = ClassConfig.objects.all()
    examList = Examname.objects.all()
    institute = Institute.objects.latest('updated_at')

    if request.method == 'POST':
        
        try:
            class_id = request.POST.get('class_name_id')
            exam_id = request.POST.get('exam_name_id')

            students = StudentProfile.objects.filter(class_id=class_id)
            exam_instance = get_object_or_404(Examname, id=exam_id)
            print(exam_instance)
            if not students.exists():
                return HttpResponse("No students found for the selected class.")
        
            # Convert images to absolute URLs
            for student in students:
                if student.student_field and student.student_field.avatar:
                    student.avatar_url = request.build_absolute_uri(student.student_field.avatar.url)
                else:
                    student.avatar_url = None
                

            ins_logo = request.build_absolute_uri(institute.institute_logo.url)
            
            
            html_string = render_to_string('layout/admitcard2.html', {
                'students': students,
                'ins_logo':ins_logo,
                'exam_instance':exam_instance,
                'institute':institute
            })
            
            pdf_file = HTML(string=html_string).write_pdf()
            
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="admitcard.pdf"'
            
            return response
        except Exception as e:
            print(f"Error: {e}")
            # print(traceback.format_exc())
            return HttpResponse("An error occurred while generating the admit card.")
        
    context = {
        'classList': classList,
        'examList': examList,
        'heading': 'Exam',
        'subheading': 'Admit Print With Routine',
    }
    return render(request, 'report/admit_print_all.html',context)


def admit_card_with_routine(request): 
    classList = ClassConfig.objects.all()
    examList = Examname.objects.all()
    institute = Institute.objects.latest('updated_at')

    if request.method == 'POST':
        try:
            class_id = request.POST.get('class_name_id')
            exam_id = request.POST.get('exam_name_id')

            print(class_id,exam_id)
            
            students = StudentProfile.objects.filter(class_id=class_id)
            if not students.exists():
                messages.warning(request, "No students found for the selected class.")
                return redirect('admit_card_with_routine')
            
            student_exam_schedules = Schedule.objects.filter(
                exam_name=exam_id, 
                class_name=class_id
            ).select_related('subject_id').order_by('exam_date')
            
            if not student_exam_schedules.exists():
                messages.warning(request, "No exam schedule (routine) found for the selected class and exam.")
                return redirect('admit_card_with_routine')
            
            # Convert images to absolute URLs
            for student in students:
                if student.student_field and student.student_field.avatar:
                    student.avatar_url = request.build_absolute_uri(student.student_field.avatar.url)
                else:
                    student.avatar_url = None
                

            ins_logo = request.build_absolute_uri(institute.institute_logo.url)
            
            # border_img = request.build_absolute_uri(static('assets/img/CertificateFrame1.svg'))
            border_img = "https://demo.BIDYATekbd.online/static/assets/img/CertificateFrame1.svg"

            
            html_string = render_to_string('layout/admitcard.html', {
                'students': students,
                'ins_logo':ins_logo,
                'exam_schedules': student_exam_schedules,
                'border_img': border_img
            })
            
            pdf_file = HTML(string=html_string).write_pdf()
            
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="admitcard.pdf"'
            
            return response
        except Exception as e:
            print(f"Error: {e}")
            # print(traceback.format_exc())
            return HttpResponse("An error occurred while generating the admit card.")
    
    context = {
        'classList': classList,
        'examList': examList,
        'heading': 'Exam',
        'subheading': 'Admit Print With Routine',
    }
    
    return render(request, 'report/admit_print_with_routine.html', context)



# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
# def admit_card_without_routine(request):
#     current_year = str(datetime.now().year)
#     admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
#     classList = ClassConfig.objects.all()
#     examList = Examname.objects.filter(academic_year=admission_year)
#     latest_institute = Institute.objects.latest('updated_at')
#     studentlist=None
#     exam=None
#     scheduleList=None
#     if request.method =='POST':
#         class_id = request.POST.get("class_name_id")
#         exam_id=request.POST.get("exam_name_id")
#         try:
#             exam = Examname.objects.get(id=exam_id)
#             scheduleList =Schedule.objects.filter(exam_name=exam)
#             studentlist = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")) 
#         except Examname.DoesNotExist:
#             pass 
#     context={
#         'range_limit': range(60),
#         'heading':'Exam',
#         'subheading':'Admit Card',
#         'examList':examList,
#         'studentlist':studentlist,
#         'classList':classList,
#         'latest_institute':latest_institute,
#         'exam':exam,
#         'scheduleList':scheduleList
#     }
#     return render(request, 'report/admit_print_all.html',context) 

# @login_required(login_url='login')
# @user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
# def admit_card_with_routine(request):
#     current_year = str(datetime.now().year)
#     admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
#     classList = ClassConfig.objects.all()
#     examList = Examname.objects.filter(academic_year=admission_year)
#     latest_institute = Institute.objects.latest('updated_at')
#     studentlist=None
#     exam=None
#     scheduleList=None
#     if request.method =='POST':
#         class_id = request.POST.get("class_name_id")
#         exam_id=request.POST.get("exam_name_id")
#         try:
#             exam = Examname.objects.get(id=exam_id)
#             scheduleList =Schedule.objects.filter(exam_name=exam)
#             studentlist = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")) 
#         except Examname.DoesNotExist:
#             pass 
#     context={
#         'range_limit': range(60),
#         'heading':'Exam',
#         'subheading':'Admit Card',
#         'examList':examList,
#         'studentlist':studentlist,
#         'classList':classList,
#         'latest_institute':latest_institute,
#         'exam':exam,
#         'scheduleList':scheduleList
#     }

#     return render(request, 'report/admit_print_with_routine.html',context) 

from django.template.loader import render_to_string
from weasyprint import HTML
from urllib.error import URLError 

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def seatplan(request):
    classList = ClassConfig.objects.all()
    examList = Examname.objects.all().order_by('-academic_year__name', 'name')

    if request.method == 'POST':
        institute = Institute.objects.latest('updated_at')
        class_id = request.POST.get('class_name_id')
        exam_id = request.POST.get('exam_name_id')
        print(class_id, exam_id)

        # Fetch relevant data based on the selected class, exam, and section
        items = StudentProfile.objects.filter(
            class_id=class_id
        ).select_related('student_field', 'class_id')

        # Add the additional details to each item for rendering
        for item in items:
            item.student_name = item.student_field.name
            item.exam_name = Examname.objects.filter(
                id=exam_id
            ).first()
            item.ins_name = institute.institute_name
            item.ins_address = institute.institute_address
            item.ins_logo = request.build_absolute_uri(institute.institute_logo.url)
            item.class_id = item.class_id
            item.section_id = item.class_id.section_id.name if item.class_id.section_id else ""
            item.roll_id = item.roll_no
            try:
                item.image_url = request.build_absolute_uri(item.student_field.avatar.url) if item.student_field.avatar else ""
            except URLError as e:
                print(f"Error fetching image: {e}")

        
        # Render the HTML template with the context data
        html_string = render_to_string('layout/seatpaln.html', {'items': items})

        # Convert the HTML to a PDF using WeasyPrint
        pdf_file = HTML(string=html_string).write_pdf()

        # Create a response to download the PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="seatplan.pdf"'  # Prompts download

        return response

    context = {
        'heading': 'Exam',
        'subheading': 'Seat Plan',
        'examList': examList,
        'classList': classList,
    }
    return render(request, 'exams/seatplan/seatplan.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"teacher", roles=['Manager','HR','DataEntry']))
def get_class_subjects(request):
    class_id = request.GET.get('class_id')
    class_instance = get_object_or_404(ClassConfig, pk=class_id)
    sub_instance = class_instance.class_group_id
    print("ClassGroupConfig:", sub_instance, sub_instance.id) 
    subjects = SubjectConfig.objects.filter(class_id=sub_instance).values('id', 'subject_id__name', 'subject_id__id')
    print("Subjects found:", list(subjects))  
    subjects_list = list(subjects)
    return JsonResponse(subjects_list, safe=False)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"teacher", roles=['Manager','HR','DataEntry']))
@csrf_exempt 
def get_mark_subjects(request):
    id_check = request.POST.get('id')
    mark_id = request.POST.get('mark_id')
    mark = request.POST.get('value')
    mode_id = id_check.split('_')
    student_id = mode_id[0]  
    subject_id = mode_id[1]  
    exam_id = mode_id[2] 

    student_instance = get_object_or_404(StudentProfile, pk=student_id)
    admission_year = student_instance.admission_year_id  # student থেকে নাও
    subject_instance = get_object_or_404(SubjectConfig, pk=subject_id)
    exam_instance = get_object_or_404(Examname, pk=exam_id)
    mark_instance = Mark_config.objects.get(subject_conf_id=subject_instance, mark_type_id=mark_id)
    pass_mark = float(mark_instance.pass_mark)
    mark = math.ceil(float(mark))
    passed = mark >= pass_mark
    updated_values = {'mark': mark, 'check_mark': passed}
    try:
        time.sleep(0.1)
        obj, created = Subject_mark.objects.update_or_create(
            examname_id=exam_instance, student_id=student_instance, mark_id=mark_instance,
            defaults=updated_values, academic_year=admission_year
        )
    except ValidationError as e:
        error_message = str(e)
        return JsonResponse({'error': error_message}, status=400) 

    return JsonResponse({'msg':'success'}, safe=False)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"teacher", roles=['Manager','HR','DataEntry']))
def mark_list(request):
    exam_list = Examname.objects.all()  # সব exam দেখাবে
    class_list = []
    exam_instance, class_instance, subject_instance, studentList, mark_conf_list = None, None, None, None, None
    marks_data = []
    
    if request.user.groups.filter(name='teacher').exists():
        teacher_assigns = Routine.objects.filter(teacher_name=request.user.id)
        class_list = ClassConfig.objects.filter(id__in=teacher_assigns.values_list('class_id', flat=True)).distinct()
    else:
        class_list = ClassConfig.objects.all()

    if request.method == "POST":
        exam_id = request.POST.get('exam_name_id')
        exam_instance = get_object_or_404(Examname, pk=exam_id)
        class_id = request.POST.get('class_name_id')
        class_instance = get_object_or_404(ClassConfig, pk=class_id)
        subject_id = request.POST.get('subject_name_id')
        subject_type = SubjectConfig.objects.filter(id=subject_id).values_list('subject_type', flat=True).first()
        
        exam_admission_year = exam_instance.academic_year  # exam থেকে year নাও
        
        if subject_type in ('COMPULSARY', 'Uncountable'):
            studentList = StudentProfile.objects.filter(
                Q(class_id=class_id) & Q(student_field__status="Active") & Q(admission_year_id=exam_admission_year)
            ).order_by("roll_no")
        elif subject_type == 'CHOOSABLE':
            choosable_students = Forth_Sub.objects.filter(subject_assign_id=subject_id).values_list('student_id', flat=True)
            studentList = StudentProfile.objects.filter(
                Q(class_id=class_id) & Q(admission_year_id=exam_admission_year) &
                Q(student_field__status="Active") & Q(id__in=choosable_students)
            ).order_by("roll_no")
        else:
            studentList = StudentProfile.objects.filter(
                Q(class_id=class_id) & Q(student_field__status="Active") & Q(admission_year_id=exam_admission_year)
            ).order_by("roll_no")

        subject_instance = get_object_or_404(SubjectConfig, pk=subject_id)
        mark_conf_list = Mark_config.objects.filter(Q(class_id=class_instance.class_group_id) & Q(subject_conf_id=subject_instance))
        subject_mark_list = Subject_mark.objects.all()

        for student in studentList:
            student_marks = []
            student_subject_marks = subject_mark_list.filter(
                student_id=student,
                mark_id__subject_conf_id=subject_instance,
                examname_id=exam_instance
            )
            total_marks = 0
            for mark_config in mark_conf_list:
                mark = student_subject_marks.filter(mark_id__mark_type_id=mark_config.mark_type_id).first()
                student_marks.append(mark.mark if mark else None)
                total_marks += mark.mark if mark else 0
            student_marks.append(total_marks)
            marks_data.append({
                'student': student,
                'marks': student_marks,
            })
  
    context = {
        'exam_instance': exam_instance,
        'exam_list': exam_list,
        'class_list': class_list,
        'class_instance': class_instance,
        'subject_instance': subject_instance,
        'studentList': studentList,
        'mark_conf_list': mark_conf_list,
        'marks_data': marks_data,
        'heading': 'Result',
        'subheading': 'Mark List'
    }
    return render(request, 'exams/mark/list_mark.html', context)

    
def is_subject_pass(student_id, subject_id, exam_id):
    subject_mark_instances = Subject_mark.objects.filter(
        student_id=student_id,
        mark_id__subject_conf_id=subject_id,
        examname_id=exam_id
    )

    mark_type_check_dict = {}

    for subject_mark_instance in subject_mark_instances:
        mark_type_id = subject_mark_instance.mark_id.mark_type_id
        check_mark = subject_mark_instance.check_mark

        if mark_type_id not in mark_type_check_dict:
            mark_type_check_dict[mark_type_id] = []

        mark_type_check_dict[mark_type_id].append(check_mark)

    for mark_type_id, check_marks in mark_type_check_dict.items():
        if not all(check_marks):
            return False

    return True

def get_subject_mark(student_id, subject_id, exam_id):
    try:
        subject_mark_instances = Subject_mark.objects.filter(
            Q(student_id=student_id) & 
            Q(mark_id__subject_conf_id=subject_id) & 
            Q(examname_id=exam_id)
        ).distinct()
        
        mark_dict = {}
        for subject_mark_instance in subject_mark_instances:
            mark_dict[subject_mark_instance.mark_id.mark_type_id.name] = subject_mark_instance.mark
        
        # Check if the subject is passed or failed
        if is_subject_pass(student_id, subject_id, exam_id):
            mark_dict['status'] = 'Passed'
        else:
            mark_dict['status'] = 'Failed'
        return mark_dict if mark_dict else None
    except Subject_mark.DoesNotExist:
        return None

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))

def wide_tabulation_sheet(request):
    context = {}

    grading_rules = [
        {"min_mark": 80, "max_mark": 100, "gpa": 5, "letter": "A+"},
        {"min_mark": 70, "max_mark": 79, "gpa": 4, "letter": "A"},
        {"min_mark": 60, "max_mark": 69, "gpa": 3.5, "letter": "A-"},
        {"min_mark": 50, "max_mark": 59, "gpa": 3, "letter": "B"},
        {"min_mark": 40, "max_mark": 49, "gpa": 2, "letter": "C"},
        {"min_mark": 33, "max_mark": 39, "gpa": 1, "letter": "D"},
        {"min_mark": 0, "max_mark": 32, "gpa": 0, "letter": "F"},
    ]

    def get_grade(value, mode="marks"):
        """Returns GPA and letter grade based on marks or GPA."""
        
        if mode == "marks":  # Marks-based grading (0-100 scale)
            grading_rules = [
                {"min_mark": 80, "max_mark": 100, "gpa": 5, "letter": "A+"},
                {"min_mark": 70, "max_mark": 79, "gpa": 4, "letter": "A"},
                {"min_mark": 60, "max_mark": 69, "gpa": 3.5, "letter": "A-"},
                {"min_mark": 50, "max_mark": 59, "gpa": 3, "letter": "B"},
                {"min_mark": 40, "max_mark": 49, "gpa": 2, "letter": "C"},
                {"min_mark": 33, "max_mark": 39, "gpa": 1, "letter": "D"},
                {"min_mark": 0, "max_mark": 32, "gpa": 0, "letter": "F"},
            ]
        else:  # GPA-based grading (0-5 scale)
            grading_rules = [
                {"min_mark": 5.00, "max_mark": 5.00, "letter": "A+"},
                {"min_mark": 4.00, "max_mark": 4.99, "letter": "A"},
                {"min_mark": 3.50, "max_mark": 3.99, "letter": "A-"},
                {"min_mark": 3.00, "max_mark": 3.49, "letter": "B"},
                {"min_mark": 2.00, "max_mark": 2.99, "letter": "C"},
                {"min_mark": 1.00, "max_mark": 1.99, "letter": "D"},
                {"min_mark": 0.00, "max_mark": 0.99, "letter": "F"},
            ]

        for rule in grading_rules:
            if rule["min_mark"] <= value <= rule["max_mark"]:
                return rule.get("gpa", None), rule["letter"]
        
        return None, "F"


    if request.method == 'POST':
        exam_name_id = request.POST.get('exam_name_id')
        class_name_id = request.POST.get('class_name_id')

        if exam_name_id and class_name_id:
            exam_instance = get_object_or_404(Examname, id=exam_name_id)
            class_instance = get_object_or_404(ClassConfig, id=class_name_id)
            class_group_instance = get_object_or_404(ClassGroupConfig, id=class_instance.class_group_id.id)

            admission_year = Admission_Year.objects.first()
            students = StudentProfile.objects.filter(class_id=class_instance)
            subject_mark_dict = {}
            unique_mark_types = {"MCQ", "Written", "Practical", "Total"}
            overall_gpa_list = []
            subject_merge_map = {}

            # Fetch SubjectConfig using ClassGroupConfig
            subject_configs = SubjectConfig.objects.filter(class_id=class_group_instance)

            # Mapping subject merging relationships
            for subject in subject_configs:
                if subject.subject_marge:
                    subject_merge_map[subject.subject_id.name] = subject.subject_marge

            for student in students:
                subject_marks = {}
                marks = Subject_mark.objects.filter(student_id=student, examname_id=exam_instance)

                total_gpa = 0.0
                total_marks = 0  # Initialize total marks for each student
                subject_count = 0
                choosable_subject = None
                merged_subjects = {}

                for mark in marks:
                    subject_name = mark.mark_id.subject_conf_id.subject_id.name
                    mark_type = mark.mark_id.mark_type_id.name.lower()  # Normalize case to lowercase
                    obtained_marks = mark.mark
                    total_marks += obtained_marks  # Accumulate total marks across subjects

                    unique_mark_types.add(mark_type)

                    # Check if the subject should be merged
                    merge_target = subject_merge_map.get(subject_name)
                    if merge_target:
                        merged_subject_name = next(
                            (key for key, val in subject_merge_map.items() if val == merge_target), subject_name
                        )

                        # Ensure the merged subject dictionary exists
                        if merged_subject_name not in merged_subjects:
                            merged_subjects[merged_subject_name] = {"MCQ": 0, "Written": 0, "Practical": 0, "Total": 0}

                        # Ensure the mark_type key exists before updating
                        merged_subjects[merged_subject_name][mark_type] = (
                            merged_subjects[merged_subject_name].get(mark_type, 0) + obtained_marks
                        )
                        merged_subjects[merged_subject_name]["Total"] += obtained_marks
                        continue

                    # Ensure subject_marks dictionary is initialized properly
                    if subject_name not in subject_marks:
                        subject_marks[subject_name] = {"MCQ": 0, "Written": 0, "Practical": 0, "Total": 0, "gpa": 0, "letter": ""}

                    # **Ensure Practical Marks are properly assigned**
                    if mark_type == "practical":  # Make sure 'practical' matches database field
                        subject_marks[subject_name]["Practical"] += obtained_marks
                    elif mark_type == "mcq":
                        subject_marks[subject_name]["MCQ"] += obtained_marks
                    elif mark_type == "written" or mark_type == "cq":
                        subject_marks[subject_name]["Written"] += obtained_marks

                    subject_marks[subject_name]["Total"] += obtained_marks

                # Merge subject data
                subject_marks.update(merged_subjects)

                # Calculate Grades
                for subject_name, marks in subject_marks.items():
                    total_marks_for_subject = sum(
                        mark.mark_id.mark for mark in Subject_mark.objects.filter(
                            student_id=student, examname_id=exam_instance,
                            mark_id__subject_conf_id__subject_id__name=subject_name
                        )
                    )

                    # Handle merged subjects' total marks correctly
                    if subject_name in subject_merge_map:
                        total_marks_for_subject *= 2  # Adjusting max marks for merged subjects

                    percentage = (marks["Total"] / total_marks_for_subject) * 100 if total_marks_for_subject > 0 else 0
                    gpa, letter = get_grade(percentage)
                    marks["gpa"] = gpa
                    marks["letter"] = letter

                    # Check if the subject is a CHOOSABLE (4th Subject)
                    subject_config = SubjectConfig.objects.filter(subject_id__name=subject_name).first()
                    if subject_config and subject_config.subject_type == "CHOOSABLE":
                        choosable_subject = (gpa, subject_name)

                    total_gpa += gpa
                    subject_count += 1

                # Apply 4th Subject Rule
                if choosable_subject:
                    gpa, subject_name = choosable_subject
                    if gpa > 2:
                        total_gpa += (gpa - 2)

                # Calculate final GPA without percentage-based scaling
                overall_gpa = total_gpa / subject_count if subject_count > 0 else 0
                overall_gpa = min(overall_gpa, 5)
                overall_gpa = round(overall_gpa, 2)

                # Assign correct letter grade based on GPA directly
                _, overall_letter = get_grade(overall_gpa, mode="gpa")

                overall_gpa_list.append((student, overall_gpa))

                # Store total marks in subject_mark_dict
                subject_mark_dict[student] = {
                    "subject_marks": subject_marks,
                    "overall_gpa": overall_gpa,
                    "overall_letter": overall_letter,
                    "total_marks": total_marks,  # Corrected: Sum of all subjects' marks
                    "roll_no": student.roll_no  # Ensuring roll number is stored properly
                }

            # Calculate Merit List
            overall_gpa_list.sort(key=lambda x: x[1], reverse=True)
            merit_dict = {student: rank + 1 for rank, (student, _) in enumerate(overall_gpa_list)}

            context.update({
                'exam_instance': exam_instance,
                'class_instance': class_instance,
                'admission_year': admission_year,
                'subject_mark_dict': subject_mark_dict,
                'unique_mark_type': list(unique_mark_types),
                'merit_dict': merit_dict,
            })

    context.update({
        'exam_list': Examname.objects.all(),
        'class_list': ClassConfig.objects.all(),
    })

    return render(request, 'exams/mark/tabulation_sheet.html', context)


def narrow_tabulation_report(request):
    """Handles the narrow tabulation report ensuring consistency with the wide tabulation sheet."""
    admission_year = Admission_Year.objects.latest("updated_at")

    exam_list = Examname.objects.filter(academic_year=admission_year)
    class_list = ClassConfig.objects.all()

    exam_instance, class_instance, students, subjects_list, subject_mark_dict = None, None, [], [], {}

    def get_grade(value, mode="marks"):
        """Returns GPA and letter grade based on marks or GPA."""
        grading_rules = [
            {"min_mark": 80, "max_mark": 100, "gpa": 5, "letter": "A+"},
            {"min_mark": 70, "max_mark": 79, "gpa": 4, "letter": "A"},
            {"min_mark": 60, "max_mark": 69, "gpa": 3.5, "letter": "A-"},
            {"min_mark": 50, "max_mark": 59, "gpa": 3, "letter": "B"},
            {"min_mark": 40, "max_mark": 49, "gpa": 2, "letter": "C"},
            {"min_mark": 33, "max_mark": 39, "gpa": 1, "letter": "D"},
            {"min_mark": 0, "max_mark": 32, "gpa": 0, "letter": "F"},
        ] if mode == "marks" else [
            {"min_mark": 5.00, "max_mark": 5.00, "letter": "A+"},
            {"min_mark": 4.00, "max_mark": 4.99, "letter": "A"},
            {"min_mark": 3.50, "max_mark": 3.99, "letter": "A-"},
            {"min_mark": 3.00, "max_mark": 3.49, "letter": "B"},
            {"min_mark": 2.00, "max_mark": 2.99, "letter": "C"},
            {"min_mark": 1.00, "max_mark": 1.99, "letter": "D"},
            {"min_mark": 0.00, "max_mark": 0.99, "letter": "F"},
        ]

        for rule in grading_rules:
            if rule["min_mark"] <= value <= rule["max_mark"]:
                return rule.get("gpa", None), rule["letter"]

        return None, "F"

    if request.method == "POST":
        exam_id = request.POST.get("exam_name_id")
        exam_instance = get_object_or_404(Examname, pk=exam_id)
        class_id = request.POST.get("class_name_id")
        class_instance = get_object_or_404(ClassConfig, pk=class_id)

        students = StudentProfile.objects.filter(
            class_id=class_instance,
            admission_year_id=admission_year.id,
            student_field__status="Active"
        ).order_by("roll_no")

        subjects_list = list(SubjectConfig.objects.filter(class_id=class_instance.class_group_id)
                             .values("id", "subject_id__name", "subject_type"))

        subject_mark_dict = {}

        for student in students:
            subject_marks = {}
            total_marks = 0
            total_gpa = 0
            subject_count = 0
            optional_gpa_bonus = 0
            choosable_subject = None  # Track the optional subject

            for subject in subjects_list:
                subject_name = subject["subject_id__name"]
                is_optional = subject["subject_type"] == "CHOOSABLE"

                marks = Subject_mark.objects.filter(
                    student_id=student,
                    examname_id=exam_instance,
                    mark_id__subject_conf_id__subject_id__name=subject_name
                )

                # ✅ Initialize Mark Types (Including Practical)
                subject_marks[subject_name] = {
                    "MCQ": 0, "CQ": 0, "Practical": 0, "Total": 0, "gpa": 0, "letter": ""
                }

                # ✅ Categorize marks correctly (MCQ, CQ, Practical)
                for mark in marks:
                    mark_type = mark.mark_id.mark_type_id.name.upper()

                    if mark_type == "MCQ":
                        subject_marks[subject_name]["MCQ"] += mark.mark
                    elif mark_type in ["CQ", "WRITTEN"]:
                        subject_marks[subject_name]["CQ"] += mark.mark
                    elif mark_type == "PRACTICAL":
                        subject_marks[subject_name]["Practical"] += mark.mark

                    subject_marks[subject_name]["Total"] += mark.mark

                # ✅ Calculate GPA & Letter Grade
                total_marks_for_subject = sum(
                    mark.mark_id.mark for mark in Subject_mark.objects.filter(
                        student_id=student, examname_id=exam_instance,
                        mark_id__subject_conf_id__subject_id__name=subject_name
                    )
                )

                percentage = (subject_marks[subject_name]["Total"] / total_marks_for_subject) * 100 if total_marks_for_subject > 0 else 0
                gpa, letter = get_grade(percentage)

                subject_marks[subject_name]["gpa"] = gpa
                subject_marks[subject_name]["letter"] = letter

                # ✅ Accumulate Total Marks
                total_marks += subject_marks[subject_name]["Total"]

                # ✅ Handling Optional Subject GPA Calculation Correctly
                if is_optional:
                    choosable_subject = (gpa, subject_name)  # Track the optional subject
                else:
                    total_gpa += gpa
                    subject_count += 1

            # ✅ Apply 4th Subject Rule
            if choosable_subject:
                gpa, subject_name = choosable_subject
                if gpa > 2:
                    total_gpa += (gpa - 2)  # ✅ Add only extra GPA above 2

            # ✅ Final GPA Calculation Following Wide Tabulation
            overall_gpa = total_gpa / subject_count if subject_count > 0 else 0
            overall_gpa = min(overall_gpa, 5)
            overall_gpa = round(overall_gpa, 2)
            _, overall_letter = get_grade(overall_gpa, mode="gpa")

            # ✅ Store in Dictionary
            subject_mark_dict[student] = {
                "subject_marks": subject_marks,
                "total_marks": total_marks,
                "overall_gpa": overall_gpa,
                "overall_letter": overall_letter,
            }

    context = {
        "exam_list": exam_list,
        "class_list": class_list,
        "exam_instance": exam_instance,
        "class_instance": class_instance,
        "admission_year": admission_year,
        "students": students,
        "subjects_list": subjects_list,
        "subject_mark_dict": subject_mark_dict,
    }

    return render(request, "exams/mark/tabulation_sheet_narrow.html", context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))


def progress_report(request):
    # Fetch the latest admission year
    admission_year = Admission_Year.objects.latest('updated_at')

    # Get available exams and classes
    exam_list = Examname.objects.filter(academic_year=admission_year)
    class_list = ClassConfig.objects.all()

    context = {
        'exam_list': exam_list,
        'class_list': class_list,
        'heading': 'Result',
        'subheading': 'Progress Report'
    }

    # Function to determine grades and GPA
    def get_grade(value, mode="marks"):
        grading_rules = [
            {"min_mark": 80, "max_mark": 100, "gpa": 5, "letter": "A+"},
            {"min_mark": 70, "max_mark": 79, "gpa": 4, "letter": "A"},
            {"min_mark": 60, "max_mark": 69, "gpa": 3.5, "letter": "A-"},
            {"min_mark": 50, "max_mark": 59, "gpa": 3, "letter": "B"},
            {"min_mark": 40, "max_mark": 49, "gpa": 2, "letter": "C"},
            {"min_mark": 33, "max_mark": 39, "gpa": 1, "letter": "D"},
            {"min_mark": 0, "max_mark": 32, "gpa": 0, "letter": "F"},
        ]

        if mode == "gpa":
            grading_rules = [
                {"min_mark": 5.00, "max_mark": 5.00, "letter": "A+"},
                {"min_mark": 4.00, "max_mark": 4.99, "letter": "A"},
                {"min_mark": 3.50, "max_mark": 3.99, "letter": "A-"},
                {"min_mark": 3.00, "max_mark": 3.49, "letter": "B"},
                {"min_mark": 2.00, "max_mark": 2.99, "letter": "C"},
                {"min_mark": 1.00, "max_mark": 1.99, "letter": "D"},
                {"min_mark": 0.00, "max_mark": 0.99, "letter": "F"},
            ]

        for rule in grading_rules:
            if rule["min_mark"] <= value <= rule["max_mark"]:
                return rule.get("gpa", 0), rule.get("letter", "F")  # ✅ Fixed KeyError

        return 0, "F"

    # Handle form submission
    if request.method == "POST":
        exam_id = request.POST.get('exam_name_id')
        class_id = request.POST.get('class_name_id')

        # Retrieve selected exam and class
        exam_instance = get_object_or_404(Examname, pk=exam_id)
        class_instance = get_object_or_404(ClassConfig, pk=class_id)
        class_group_instance = class_instance.class_group_id

        # Get all active students in the selected class
        students = StudentProfile.objects.filter(
            Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")
        ).order_by("roll_no")

        results = []
        subject_mark_dict = {}

        for student in students:
            # Get all compulsory and optional subjects
            compulsory_subjects = SubjectConfig.objects.filter(class_id=class_group_instance, subject_type='COMPULSARY')
            optional_subjects = Forth_Sub.objects.filter(student_id=student, forth_type="OPTIONAL")

            all_subjects = list(compulsory_subjects) + [opt.sub_conf_id for opt in optional_subjects]

            total_gpa_without_optional = 0
            compulsory_subject_count = 0
            optional_gpa = 0
            optional_found = False
            total_marks = 0
            choosable_subjects = {}

            # Store subject marks for this student
            subject_mark_dict[student.roll_no] = {}

            for subject in all_subjects:
                # Fetch subject marks
                subject_marks = Subject_mark.objects.filter(
                    student_id=student, examname_id=exam_instance, mark_id__subject_conf_id=subject
                )

                total_subject_marks = sum(mark.mark for mark in subject_marks)
                full_marks = subject.mark if subject.mark is not None else 100
                percentage = (total_subject_marks / full_marks) * 100 if full_marks > 0 else 0
                gpa, letter = get_grade(percentage)

                # Check if it's an optional subject
                is_optional = optional_subjects.filter(sub_conf_id=subject).exists()

                if is_optional:
                    optional_found = True
                    optional_gpa = max(optional_gpa, gpa)
                    choosable_subjects[subject.subject_id.name] = {
                        "Letter": letter,
                        "GPA": gpa,
                        "GPA_if_counted": max(0, gpa - 2)
                    }
                else:
                    total_gpa_without_optional += gpa
                    compulsory_subject_count += 1

                total_marks += total_subject_marks

                subject_mark_dict[student.roll_no][subject.subject_id.name] = {
                    "Letter": letter,
                    "GPA": gpa,
                    "Total Marks": total_subject_marks
                }

            # Calculate GPA
            gpa_without_optional = round(total_gpa_without_optional / compulsory_subject_count, 2) if compulsory_subject_count else 0
            total_gpa_with_optional = total_gpa_without_optional + (max(0, optional_gpa - 2))
            final_gpa = round(total_gpa_with_optional / compulsory_subject_count, 2)
            final_letter = get_grade(final_gpa, mode="gpa")[1]

            # Store student result
            results.append({
                'student_name': student.student_field.name,
                'roll_no': student.roll_no,
                'gpa_without_optional': gpa_without_optional,
                'gpa_with_optional': final_gpa,
                'grade': final_letter,
                'choosable_subjects': choosable_subjects
            })

        # Update context with results
        context.update({
            'exam_instance': exam_instance,
            'class_instance': class_instance,
            'results': results,
            'subject_mark_dict': subject_mark_dict
        })

    return render(request, 'exams/mark/progress_report.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager', 'HR']))
def merit_list(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    exam_list = Examname.objects.filter(academic_year=admission_year)
    class_list = ClassConfig.objects.all()
    exam_instance, class_instance, studentList, unique_mark_type, subjects_list, subject_mark_dict, unique_mark_type_count, subject_marks, total_full_marks = None, None, None, None, None, None, None, None, None
    result = []
    
    if request.method == "POST":
        exam_id = request.POST.get('exam_name_id')
        exam_instance = get_object_or_404(Examname, pk=exam_id)
        class_id = request.POST.get('class_name_id')
        class_instance = get_object_or_404(ClassConfig, pk=class_id)
        studentList = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")).order_by("roll_no")
        mark_conf_list = Mark_config.objects.filter(class_id=class_instance.class_group_id.class_id)
        unique_mark_types_ids = mark_conf_list.values_list('mark_type_id', flat=True).distinct()
        unique_mark_type = Mark_type.objects.filter(id__in=unique_mark_types_ids).values_list('name', flat=True)
        unique_mark_type_count = Mark_type.objects.filter(id__in=unique_mark_types_ids).count()
        sub_instance = class_instance.class_group_id.class_id
        compulsory_subjects = SubjectConfig.objects.filter(class_id=sub_instance, subject_type='COMPULSARY')
        subjects_list = list(compulsory_subjects.values('id', 'subject_id__name'))

        subject_marks = {}
        subject_mark_dict = {}

        for student in studentList:
            choosable_subjects = Choosable_Subject.objects.filter(student=student).values_list('subject_assign', flat=True)
            all_subjects = compulsory_subjects | SubjectConfig.objects.filter(id__in=choosable_subjects)
            all_subjects_list = list(all_subjects.values('id', 'subject_id__name'))

            total_full_marks = sum(SubjectConfig.objects.filter(id=subject['id']).first().mark for subject in all_subjects_list)

            subject_marks[student] = {}
            subject_mark_dict[student] = {}
            total_marks_for_student = 0
            total_gpa = 0
            result_status = None
            subject_gpas = []

            for subject in all_subjects_list:
                subject_mark_dict[student][subject['subject_id__name']] = get_subject_mark(student.id, subject['id'], exam_instance)
                subject_marks = subject_mark_dict[student][subject['subject_id__name']]
                status = subject_marks.get('status', 'Unknown')

                if status == 'Passed':
                    filtered_subject_marks = {key: value for key, value in subject_marks.items() if key != 'status'}
                    total_marks_for_subject = sum(filtered_subject_marks.values()) if filtered_subject_marks else 0
                    total_marks_for_student += total_marks_for_subject
                else:
                    total_marks_for_subject = 0

                num_subjects = len(subjects_list)
                grading_rule = Graderule.objects.filter(min_mark__lte=total_marks_for_subject, max_mark__gte=total_marks_for_subject).first()

                gpa_for_subject = grading_rule.gpa if grading_rule else 0
                subject_gpas.append(gpa_for_subject)

            if any(gpa == 0 for gpa in subject_gpas):
                gpa = 0
                result_status = 'FAILED'
            else:
                total_gpa = sum(subject_gpas)
                gpa = round(total_gpa / num_subjects, 2)
                result_status = 'PASSED'

            result.append({
                'student_name': student.student_field.name,
                'student_roll': student.roll_no,
                'total_marks': total_marks_for_student,
                'gpa': gpa,
                'status': result_status,
                'merit_list': 0
            })

    sorted_result = sorted(result, key=lambda x: x['total_marks'], reverse=True)

    merit_list_number = 1
    for entry in sorted_result:
        entry['merit_list'] = merit_list_number
        merit_list_number += 1

    context = {
        'exam_list': exam_list,
        'class_list': class_list,
        'exam_instance': exam_instance,
        'class_instance': class_instance,
        'admission_year': admission_year,
        'studentList': studentList,
        'unique_mark_type': unique_mark_type,
        'unique_mark_type_count': unique_mark_type_count,
        'subjects_list': subjects_list,
        'total_full_marks': total_full_marks,
        'subject_mark_dict': subject_mark_dict,
        'subject_marks': subject_marks,
        'result': sorted_result,  # Pass the sorted result here
        'heading': 'Result',
        'subheading': 'Merit List'
    }

    return render(request, 'exams/mark/merit_list.html', context)
    

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
@csrf_exempt 
def get_subject_name(request):
    class_id = request.GET.get('class_id')
    class_instance= get_object_or_404(StudentClass, pk=class_id)
    subjects = SubjectConfig.objects.filter(class_id=class_instance).values('id', 'subject_id__name')
    subjects_list = list(subjects)

    return JsonResponse(subjects_list, safe=False)


def encode_special_characters(message):
    special_characters = {'&': '%26', '$': '%24', '@': '%40', '+': '%2B'}
    for char, encoded_char in special_characters.items():
        message = message.replace(char, encoded_char)
    return message


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def result_sms(request, exam_instance_id, class_id_list):
    try:
        exam_instance = get_object_or_404(Examname, pk=exam_instance_id)
        admission_year = Admission_Year.objects.latest('updated_at')
        # class_list = ClassConfig.objects.filter(academic_year=admission_year)
        class_list = ClassConfig.objects.filter(academic_year=admission_year, class_group_id__class_id__in=class_id_list)
        
        # studentList = StudentProfile.objects.filter(Q(admission_year_id=admission_year) & Q(student_field__status="Active")).order_by("roll_no")
        studentList = StudentProfile.objects.filter(
            Q(admission_year_id=admission_year) & 
            Q(student_field__status="Active") & 
            Q(class_id__class_group_id__class_id__in=class_id_list)
        ).order_by("roll_no")
        
        
        compulsory_subjects = SubjectConfig.objects.filter(class_id__in=class_list.values_list('class_group_id__class_id', flat=True), subject_type='COMPULSARY')
        subjects_list = list(compulsory_subjects.values('id', 'subject_id__name'))
        result = []
        subject_marks = {}
        subject_mark_dict = {}

        for student in studentList:
            student_class_id = student.class_id.class_group_id.class_id
            compulsory_subjects = SubjectConfig.objects.filter(class_id=student_class_id, subject_type='COMPULSARY')
            try:
                choosable_subjects = Choosable_Subject.objects.filter(student=student).values_list('subject_assign', flat=True)
            except:
                choosable_subjects = Choosable_Subject.objects.none()
                
            all_subjects = compulsory_subjects | SubjectConfig.objects.filter(id__in=choosable_subjects)
            all_subjects_list = list(all_subjects.values('id', 'subject_id__name'))

            total_full_marks = 0

            for subject in all_subjects_list:
                subject_config = SubjectConfig.objects.filter(id=subject['id']).first()
                if subject_config:
                    total_full_marks += subject_config.mark

            subject_marks[student] = {}
            subject_mark_dict[student] = {}
            total_marks_for_student = 0
            total_gpa = 0
            result_status = None
            subject_gpas = []
            for subject in all_subjects_list:
                subject_mark_dict[student][subject['subject_id__name']] = get_subject_mark(student.id, subject['id'], exam_instance)
                subject_marks = subject_mark_dict[student][subject['subject_id__name']]
                status = subject_marks.get('status', 'Unknown')

                if status == 'Passed':
                    filtered_subject_marks = {key: value for key, value in subject_marks.items() if key != 'status'}
                    total_marks_for_subject = sum(filtered_subject_marks.values()) if filtered_subject_marks else 0
                    total_marks_for_student += total_marks_for_subject
                else:
                    total_marks_for_subject = 0

                num_subjects = len(all_subjects)
                grading_rule = Graderule.objects.filter(min_mark__lte=total_marks_for_subject, max_mark__gte=total_marks_for_subject).first()

                if grading_rule:
                    gpa_for_subject = grading_rule.gpa
                    grade_name = grading_rule.grade_name
                else:
                    gpa_for_subject = 0
                    grade_name = 'N/A'

                subject_gpas.append(gpa_for_subject)
                subject_mark_dict[student][subject['subject_id__name']]['grade_name'] = grade_name
                
            if any(gpa == 0 for gpa in subject_gpas):
                gpa = 0
                result_status = 'FAILED'
            else:
                total_gpa = sum(subject_gpas)
                gpa = round(total_gpa / num_subjects, 2)
                result_status = 'PASSED'

            result.append({
                'student_name': student.student_field.name.title(),
                'student_id': student.id,
                'total_marks': total_marks_for_student,
                'gpa': gpa,
                'status': result_status,
                'merit_list': 0,
                'subject_mark_dict': subject_mark_dict[student],
                'grade_name': grade_name
            })
            # print(result)
            template = SMSTemplateNotification.objects.filter(
                            notification_type='Exam Result',
                            notification_status='Active'
                            ).first()
            
            for student_result in result:
                student_name = student_result['student_name']
                total_marks = student_result['total_marks']
                gpa = student_result['gpa']
                status = student_result['status']
                subject_details = student_result['subject_mark_dict']
                subject_LTR = ', '.join([f"{subject}: {marks['grade_name']}" for subject, marks in subject_details.items()])
                
                formatted_result = template.body.format(
                                    student_name=student_name,
                                    total_marks=total_marks,
                                    status=status,
                                    gpa=gpa,
                                    subject_LTR=subject_LTR
                                    )
                
            student_id = student_result['student_id']
            student_instance = StudentProfile.objects.get(id=student_id)
            student_number = student_instance.parent_id.phone_number
            formatted_number = '880' + student_number.lstrip('0')
            if template:
                sms_body = f"{formatted_result}"
                # sms_body = encode_special_characters(formatted_result)
                sms_count = count_sms(sms_body)
                sms_limit_obj = SMSUsage.objects.filter(Msg_type='NONMASKING').first()
                if sms_limit_obj.total_sms < 1:
                    print('SMS LIMIT OVER')
                else:
                    receiver = f'{formatted_number}'
                    send_sms(receiver , sms_body)
                    sms_limit_obj.total_sms -= sms_count
                    sms_limit_obj.save()
                    SMS.objects.create(mobile=student_number, title='Result', msg=sms_body, created_by=request.user)

        messages.success(request, 'Messages sent successfully ! ! !')
        return redirect ('notification_sms')
    except Exception as e:
            messages.error(request, 'There was an error sending the messages.')
    


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def generate_certificate_report(request, student_id): 
    institute=Institute.objects.latest('id')
    student= StudentProfile.objects.get(id=student_id)
    context={
        'institute':institute,
        'student':student
    }
    return render(request, 'exams/mark/student_certificate_print.html',context) 


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_certificate(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    classList = StudentClass.objects.filter(academic_year=admission_year)
    studentlist=None
    if request.method == 'POST':
        class_id =request.POST.get("class_id")
        class_instance= get_object_or_404(StudentClass, pk=class_id)
        studentlist = StudentProfile.objects.filter(Q(class_id__class_group_id__class_id=class_instance) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")).order_by("class_id","roll_no")
        # return redirect('list_testmonial')

    context={
    'classList':classList,
    'studentlist':studentlist,
    'heading':'Result',
    'subheading':'Certificate',

    }
    return render(request, 'exams/mark/student_certificate.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def mark_blank_sheet(request):
    current_year = str(datetime.now().year)
    admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
    exam_list= Examname.objects.all()
    class_list= ClassConfig.objects.all()
    institute=Institute.objects.latest('id')
    exam_instance, class_instance, subject_instance,studentList,mark_conf_list =None, None, None, None, None
    marks_data = []
    if request.method=="POST":
        exam_id = request.POST.get('exam_name_id')
        exam_instance = get_object_or_404(Examname,pk=exam_id)
        class_id = request.POST.get('class_name_id')
        class_instance = get_object_or_404(ClassConfig,pk=class_id)
        # subject_id = request.POST.get('subject_name_id')
        # subject_type = SubjectConfig.objects.filter(id=subject_id).values_list('subject_type', flat=True).first()
        # if subject_type == 'COMPULSARY':
        studentList = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")).order_by("roll_no")
        # elif subject_type == 'CHOOSABLE':
        #     choosable_students = Choosable_Subject.objects.filter(subject_assign_id=subject_id).values_list('student_id', flat=True)
        #     studentList = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(id__in=choosable_students)).order_by("roll_no")
        # subject_instance = get_object_or_404(SubjectConfig,pk=subject_id)
        # mark_conf_list = Mark_config.objects.filter(Q(class_id=class_instance.class_group_id.class_id) & Q(subject_conf_id=subject_instance))
        # subject_mark_list= Subject_mark.objects.all()

        # for student in studentList:
        #     student_marks = []

        #     student_subject_marks = subject_mark_list.filter(
        #         student_id=student,
        #         mark_id__subject_conf_id=subject_instance,
        #         examname_id=exam_instance
        #     )
        #     total_marks = 0
        #     for mark_config in mark_conf_list:
        #         mark = student_subject_marks.filter(mark_id__mark_type_id=mark_config.mark_type_id).first()
        #         student_marks.append(mark.mark if mark else None)
        #         total_marks += mark.mark if mark else 0

        #     student_marks.append(total_marks)

        #     marks_data.append({
        #         'student': student,
        #         'marks': student_marks,
        #     })
    context={
    'institute':institute,
    'exam_instance':exam_instance,
    'exam_list': exam_list,
    'class_list':class_list,
    'class_instance':class_instance,
    'studentList':studentList,
    # 'subject_instance':subject_instance,
    # 'mark_conf_list':mark_conf_list,
    # 'marks_data': marks_data,
    'heading':'Exam',
    'subheading':'Mark Blank Sheet',
    }
    return render(request, 'exams/mark/blank_mark_print.html',context) 


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def exam_signature_sheet(request):
    current_year = str(datetime.now().year)
    admission_year, _ = Admission_Year.objects.get_or_create(name=current_year)
    exam_list= Examname.objects.filter(academic_year=admission_year)
    class_list= ClassConfig.objects.all()
    exam_instance, class_instance,studentList =None, None, None
    
    if request.method=="POST":
        exam_id = request.POST.get('exam_name_id')
        exam_instance = get_object_or_404(Examname,pk=exam_id)
        class_id = request.POST.get('class_name_id')
        class_instance = get_object_or_404(ClassConfig,pk=class_id)
        studentList = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")).order_by("roll_no")
       
    context={
    'exam_instance':exam_instance,
    'exam_list': exam_list,
    'class_list':class_list,
    'class_instance':class_instance,
    'studentList':studentList,
    'heading':'Exam',
    'subheading':'Exam Signature Sheet',
    }
    return render(request, 'exams/mark/exam_signature.html',context) 


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def exam_fee_sheet(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    exam_list= Examname.objects.filter(academic_year=admission_year)
    class_list= ClassConfig.objects.filter(academic_year=admission_year)
    exam_instance, class_instance,studentList =None, None, None
    
    if request.method=="POST":
        exam_id = request.POST.get('exam_name_id')
        exam_instance = get_object_or_404(Examname,pk=exam_id)
        class_id = request.POST.get('class_name_id')
        class_instance = get_object_or_404(ClassConfig,pk=class_id)
        studentList = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")).order_by("roll_no")
       
    context={
    'exam_instance':exam_instance,
    'exam_list': exam_list,
    'class_list':class_list,
    'class_instance':class_instance,
    'studentList':studentList,
    'heading':'Exam',
    'subheading':'Exam Signature Sheet',
    }
    return render(request, 'exams/mark/exam_fee_sheet.html',context) 



@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def oral_mark_sheet(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    exam_list= Examname.objects.filter(academic_year=admission_year)
    class_list= ClassConfig.objects.filter(academic_year=admission_year)
    exam_instance, class_instance,studentList =None, None, None
    
    if request.method=="POST":
        exam_id = request.POST.get('exam_name_id')
        exam_instance = get_object_or_404(Examname,pk=exam_id)
        class_id = request.POST.get('class_name_id')
        class_instance = get_object_or_404(ClassConfig,pk=class_id)
        studentList = StudentProfile.objects.filter(Q(class_id=class_id) & Q(admission_year_id=admission_year) & Q(student_field__status="Active")).order_by("roll_no")
       
    context={
    'exam_instance':exam_instance,
    'exam_list': exam_list,
    'class_list':class_list,
    'class_instance':class_instance,
    'studentList':studentList,
    'heading':'Exam',
    'subheading':'Oral mark Sheet',
    }
    return render(request, 'exams/mark/oral_mark_sheet.html',context) 



def student_marksheet_api(request, roll_no):
    try:
        # Fetch the student profile using the roll number
        student = get_object_or_404(StudentProfile, roll_no=roll_no)

        # Fetch the latest exam
        latest_exam = Examname.objects.latest('end_date')

        # Fetch grading rules or define default ones
        grading_rules = Graderule.objects.all()
        if not grading_rules.exists():
            grading_rules = [
                {"min_mark": 80, "max_mark": 100, "gpa": 5.0, "grade_name": "A+"},
                {"min_mark": 70, "max_mark": 79, "gpa": 4.0, "grade_name": "A"},
                {"min_mark": 60, "max_mark": 69, "gpa": 3.5, "grade_name": "A-"},
                {"min_mark": 50, "max_mark": 59, "gpa": 3.0, "grade_name": "B"},
                {"min_mark": 40, "max_mark": 49, "gpa": 2.0, "grade_name": "C"},
                {"min_mark": 33, "max_mark": 39, "gpa": 1.0, "grade_name": "D"},
                {"min_mark": 0, "max_mark": 32, "gpa": 0.0, "grade_name": "F"},
            ]
        else:
            grading_rules = [
                {"min_mark": rule.min_mark, "max_mark": rule.max_mark, "gpa": rule.gpa, "grade_name": rule.grade_name}
                for rule in grading_rules
            ]

        # Helper function to calculate GPA and grade letter
        def get_grade(percentage):
            for rule in grading_rules:
                if rule["min_mark"] <= percentage <= rule["max_mark"]:
                    return rule["gpa"], rule["grade_name"]
            return 0, "F"

        # Fetch parent details with fallback values
        parent = student.parent_id
        father_name = getattr(parent, "father_name", "N/A")
        mother_name = getattr(parent, "mother_name", "N/A")

        # Fetch date of birth from the correct model
        date_of_birth = getattr(student.student_field, "date_of_birth", "N/A")

        # Prepare the transcript data
        transcript_data = {
            "student_name": student.student_field.name,
            "roll_no": student.roll_no,
            "exam_name": latest_exam.name,
            "class_name": getattr(student.class_id, "class_name", "Unknown Class"),
            "father_name": father_name,
            "mother_name": mother_name,
            "group": getattr(student.class_id, "group", ""),
            "registration_no": student.birth_certificate_no or "N/A",
            "date_of_birth": date_of_birth,
            "institute_name": "Ratanpur Higher Secondary School",
            "center_name": "(428) Brahmanbaria",
            "serial_no": "CB 6178589",
            "additional_serial_no": "CBCS08 80864078",
            "subjects": [],
            "gpa_without_optional": 0,
            "final_gpa": 0,
            "publication_date": "June 26, 2024",
        }

        # Initialize variables for GPA calculation
        total_gpa = 0
        total_subjects = 0
        optional_gpa = 0
        optional_found = False

        # Fetch subject marks
        subject_marks = Subject_mark.objects.filter(student_id=student, examname_id=latest_exam)
        if not subject_marks.exists():
            return JsonResponse({"error": "No marks found for the student in the latest exam."}, status=404)

        # Aggregate marks by subject
        subject_aggregate = {}
        for mark in subject_marks:
            subject_name = mark.mark_id.subject_conf_id.subject_id.name
            max_marks = mark.mark_id.mark
            obtained_marks = mark.mark

            if subject_name not in subject_aggregate:
                subject_aggregate[subject_name] = {
                    "total_obtained": 0,
                    "total_max": 0,
                    "is_optional": False,
                }

            subject_aggregate[subject_name]["total_obtained"] += obtained_marks
            subject_aggregate[subject_name]["total_max"] += max_marks

            # Check if the subject is optional
            subject_config = mark.mark_id.subject_conf_id
            forth_subject = Forth_Sub.objects.filter(student_id=student, sub_conf_id=subject_config).first()
            is_optional = forth_subject and forth_subject.forth_type == "OPTIONAL"

            if is_optional:
                subject_aggregate[subject_name]["is_optional"] = True

        # Calculate grades and GPA for each subject
        for subject_name, data in subject_aggregate.items():
            total_obtained = data["total_obtained"]
            total_max = data["total_max"]
            is_optional = data["is_optional"]

            percentage = (total_obtained / total_max) * 100 if total_max > 0 else 0
            gpa, letter = get_grade(percentage)

            if is_optional:
                optional_found = True
                optional_gpa = max(optional_gpa, gpa)
            else:
                total_gpa += gpa
                total_subjects += 1

            # Add subject details to the transcript
            transcript_data["subjects"].append({
                "name": subject_name,
                "grade_point": gpa,
                "letter_grade": letter,
                "total_marks": total_max,
                "obtained_marks": total_obtained,
            })

        # Add optional GPA if applicable
        if optional_found and optional_gpa > 2:
            total_gpa += optional_gpa
            total_subjects += 1

        # Calculate GPA
        gpa_without_optional = round(total_gpa / total_subjects, 2) if total_subjects > 0 else 0
        final_gpa = min(gpa_without_optional, 5)  # Cap GPA at 5

        transcript_data["gpa_without_optional"] = gpa_without_optional
        transcript_data["final_gpa"] = final_gpa

        # Check if the request wants a PDF
        if request.GET.get('format') == 'pdf':
            html_string = render_to_string('exams/mark/transcript_template.html', {'transcript': transcript_data})
            html = HTML(string=html_string)
            with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
                html.write_pdf(target=temp_file.name)
                temp_file.seek(0)
                response = HttpResponse(temp_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="Transcript_{roll_no}.pdf"'
                return response

        # Render the HTML page if not PDF
        return render(request, 'exams/mark/transcript_template.html', {'transcript': transcript_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def result_overview(request):
    """
    Generate report for a specific class, section, and exam.
    """
    classes = ClassConfig.objects.all()
    exams = Examname.objects.all()

    students = subject_marks = student_results = []
    failed_students = absent_students = gpa_data = None
    highest_marks = lowest_marks = total_students = passed_students = failed_students_count = absent_students_count = None

    # Initialize values to prevent UnboundLocalError
    subject_fail_counts = {}

    # Initialize selected values
    selected_class_id = selected_section_id = selected_exam_id = None

    def get_grade(value, mode="marks"):
        grading_rules = [
            {"min_mark": 80, "max_mark": 100, "gpa": 5, "letter": "A+"},
            {"min_mark": 70, "max_mark": 79, "gpa": 4, "letter": "A"},
            {"min_mark": 60, "max_mark": 69, "gpa": 3.5, "letter": "A-"},
            {"min_mark": 50, "max_mark": 59, "gpa": 3, "letter": "B"},
            {"min_mark": 40, "max_mark": 49, "gpa": 2, "letter": "C"},
            {"min_mark": 33, "max_mark": 39, "gpa": 1, "letter": "D"},
            {"min_mark": 0, "max_mark": 32, "gpa": 0, "letter": "F"},
        ]

        if mode == "gpa":
            grading_rules = [
                {"min_mark": 5.00, "max_mark": 5.00, "letter": "A+"},
                {"min_mark": 4.00, "max_mark": 4.99, "letter": "A"},
                {"min_mark": 3.50, "max_mark": 3.99, "letter": "A-"},
                {"min_mark": 3.00, "max_mark": 3.49, "letter": "B"},
                {"min_mark": 2.00, "max_mark": 2.99, "letter": "C"},
                {"min_mark": 1.00, "max_mark": 1.99, "letter": "D"},
                {"min_mark": 0.00, "max_mark": 0.99, "letter": "F"},
            ]

        for rule in grading_rules:
            if rule["min_mark"] <= value <= rule["max_mark"]:
                return rule.get("gpa", 0), rule.get("letter", "F") 

        return 0, "F"

    if request.method == "POST":
        selected_class_id = request.POST.get("class_id")
        selected_exam_id = request.POST.get("exam_id")

        if selected_class_id and selected_exam_id:
            students = StudentProfile.objects.filter(
                class_id=selected_class_id
            )
            exam = Examname.objects.get(id=selected_exam_id)

            # Get marks for all subjects
            subject_marks = Subject_mark.objects.filter(
                student_id__in=students,
                examname_id=exam
            ).values(
                'student_id', 
                'mark_id__subject_conf_id__subject_id__name'
            ).annotate(
                total_marks=Sum('mark'),  # Sum of CQ, MCQ, Practical
                max_marks=Sum(F('mark_id__mark')),  # Total max marks for the subject
                min_pass=Sum(F('mark_id__pass_mark'))  # Minimum pass marks for each subject
            )

            # Fixing Subject-wise Failed Count
            for mark in subject_marks:
                subject_name = mark['mark_id__subject_conf_id__subject_id__name']
                total_marks = mark['total_marks']
                max_marks = mark['max_marks']
                min_pass = mark['min_pass']

                # Calculate the percentage
                percentage = (total_marks / max_marks) * 100 if max_marks else 0
                failed = percentage < 33 or total_marks < min_pass  # Subject is failed if <33%

                if subject_name not in subject_fail_counts:
                    subject_fail_counts[subject_name] = 0
                if failed:
                    subject_fail_counts[subject_name] += 1

            # GPA Calculation
            student_results = StudentResult.objects.filter(
                student__in=students,
                exam=exam
            )

            # Correcting GPA Distribution Based on the `progress_report` Logic
            gpa_data = {
                "gpa_5": student_results.filter(gpa=5.00).count(),
                "gpa_4_to_4_99": student_results.filter(gpa__gte=4.00, gpa__lt=5.00).count(),
                "gpa_3_5_to_3_99": student_results.filter(gpa__gte=3.50, gpa__lt=4.00).count(),
                "gpa_3_to_3_49": student_results.filter(gpa__gte=3.00, gpa__lt=3.50).count(),
                "gpa_2_to_2_99": student_results.filter(gpa__gte=2.00, gpa__lt=3.00).count(),
                "gpa_1_to_1_99": student_results.filter(gpa__gte=1.00, gpa__lt=2.00).count(),
                "gpa_below_1": student_results.filter(gpa__lt=1.00).count(),
            }


            # Failed and Absent Students
            failed_students = student_results.filter(is_pass=False).count()
            absent_students = subject_marks.filter(Q(check_mark=False)).values_list('student_id', flat=True).distinct().count()

            # Highest and Lowest Marks
            obtained_marks_list = student_results.values_list("obtained_marks", flat=True)
            highest_marks = max(obtained_marks_list) if obtained_marks_list else 0
            lowest_marks = min(obtained_marks_list) if obtained_marks_list else 0

            total_students = students.count()
            passed_students = student_results.filter(is_pass=True).count()

    context = {
        "classes": classes,
        "exams": exams,
        "total_students": total_students,
        "passed_students": passed_students,
        "failed_students": failed_students,
        "absent_students": absent_students,
        "gpa_data": gpa_data,
        "highest_marks": highest_marks,
        "lowest_marks": lowest_marks,
        "subject_wise_data": subject_fail_counts,  # No more UnboundLocalError
        "selected_class_id": selected_class_id,
        "selected_section_id": selected_section_id,
        "selected_exam_id": selected_exam_id,
        'heading': 'Result ',
        'subheading': 'Result Overview',
    }

    return render(request, "exams/mark/result_report.html", context)


from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.db.models import Count, Q

def download_result_report_pdf(request):
    """
    Generates a PDF file of the result report with the same UI as the web page.
    """
    selected_class_id = request.GET.get("class_id")
    selected_exam_id = request.GET.get("exam_id")

    # ✅ Validate Input (Ensure IDs are provided)
    if not selected_class_id or not selected_exam_id:
        return HttpResponseBadRequest("Error: Missing class_id or exam_id parameters.")

    try:
        selected_class_id = int(selected_class_id)
        selected_exam_id = int(selected_exam_id)
    except ValueError:
        return HttpResponseBadRequest("Error: Invalid class_id or exam_id format.")

    # ✅ Fetch Exam Object (Ensure it exists)
    exam = get_object_or_404(Examname, id=selected_exam_id)

    # ✅ Fetch Students
    students = StudentProfile.objects.filter(
        class_id=selected_class_id
    )

    if not students.exists():
        return HttpResponseBadRequest("Error: No students found for the selected criteria.")

    # ✅ Fetch Results
    student_results = StudentResult.objects.filter(
        student__in=students,
        exam=exam
    )

    subject_marks = Subject_mark.objects.filter(
        student_id__in=students,
        examname_id=exam
    )

    # ✅ Generate GPA Distribution
    gpa_data = {
        "4.5_and_above": student_results.filter(gpa__gte=4.5).count(),
        "4_and_above": student_results.filter(gpa__gte=4, gpa__lt=4.5).count(),
        "3.5_and_above": student_results.filter(gpa__gte=3.5, gpa__lt=4).count(),
        "3_and_above": student_results.filter(gpa__gte=3, gpa__lt=3.5).count(),
        "2.5_and_above": student_results.filter(gpa__gte=2.5, gpa__lt=3).count(),
        "2_and_above": student_results.filter(gpa__gte=2, gpa__lt=2.5).count(),
        "below_2": student_results.filter(gpa__lt=2).count(),
    }

    # ✅ Calculate Highest and Lowest Marks
    obtained_marks_list = student_results.values_list('obtained_marks', flat=True)
    obtained_marks_list = [marks for marks in obtained_marks_list if marks is not None]

    highest_marks = max(obtained_marks_list, default=0)
    lowest_marks = min(obtained_marks_list, default=0)

    # ✅ Subject-Wise Failed and Absent Data
    subject_wise_data = subject_marks.values(
        'mark_id__subject_conf_id__subject_id__name'
    ).annotate(
        total_failed=Count('id', filter=Q(mark__lt=33, check_mark=True)),
        total_absent=Count('id', filter=Q(check_mark=False)),
    )

    total_students = students.count()
    passed_students = student_results.filter(is_pass=True).count()
    failed_students_count = student_results.filter(is_pass=False).count()
    absent_students_count = subject_marks.filter(check_mark=False).values('student_id').distinct().count()

    context = {
        "total_students": total_students,
        "passed_students": passed_students,
        "failed_students": failed_students_count,
        "absent_students": absent_students_count,
        "gpa_data": gpa_data,
        "highest_marks": highest_marks,
        "lowest_marks": lowest_marks,
        "subject_wise_data": subject_wise_data,
    }

    # ✅ Render HTML Template for PDF
    html_string = render_to_string("exams/mark/result_report_pdf.html", context)

    # ✅ Generate PDF Using WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf(
        stylesheets=[CSS(string="""
            @page {
                size: A4 portrait;
                margin: 10px;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 10px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 6px;
                text-align: center;
                font-size: 9px;
            }
            th {
                background-color: #2A3F54;
                color: white;
                font-size: 10px;
            }
            .highlight {
                font-weight: bold;
                color: #1D1E4E;
            }
        """)]
    )

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=result_report.pdf"
    return response

def calculate_result(self):
    """
    Calculate the result for a student in an exam.
    """
    # Initialize variables
    is_pass = True
    total_marks = 0
    obtained_marks = 0
    subjects_details = []
    fail_count = 0

    # Get all marks for this student and exam
    subject_marks = Subject_mark.objects.filter(student_id=self.student, examname_id=self.exam)

    # Group marks by subject
    subject_grouped_marks = {}
    for subject_mark in subject_marks:
        subject_conf = subject_mark.mark_id.subject_conf_id
        if subject_conf not in subject_grouped_marks:
            subject_grouped_marks[subject_conf] = []
        subject_grouped_marks[subject_conf].append(subject_mark)

    # Process each subject
    for subject_conf, marks in subject_grouped_marks.items():
        subject_total_marks = 0
        subject_obtained_marks = 0
        subject_is_pass = True

        # Check if the subject is optional
        forth_sub = Forth_Sub.objects.filter(student_id=self.student, sub_conf_id=subject_conf).first()
        is_optional = forth_sub and forth_sub.forth_type == "OPTIONAL"

        # Process each mark configuration
        for mark in marks:
            mark_config = mark.mark_id
            if not mark_config:  # Skip if mark_config is None
                continue

            subject_total_marks += mark_config.mark

            # Check if this mark is passing
            if mark.mark < mark_config.pass_mark:
                subject_is_pass = False

            subject_obtained_marks += mark.mark

        # Check pass/fail status for the subject
        if not subject_is_pass:
            fail_count += 1
            # If the subject is compulsory, mark the student as not passed
            if not is_optional:
                is_pass = False

        # Add the subject's details to the JSON field
        percentage = (subject_obtained_marks / subject_total_marks) * 100 if subject_total_marks > 0 else 0
        grade = None
        remarks = None

        # Determine the grade based on percentage
        grading_rules = Graderule.objects.all()
        for rule in grading_rules:
            if rule.min_mark <= percentage <= rule.max_mark:
                grade = rule.gpa
                remarks = rule.remarks
                break

        # If the subject is failed, grade is 0
        if not subject_is_pass:
            grade = 0
            remarks = "Failed"

        subjects_details.append({
            "subject_name": subject_conf.subject_id.name,
            "subject_Serial": subject_conf.subject_Serial,
            "subject_marge": subject_conf.subject_marge,
            "subject_type": subject_conf.subject_type,
            "total_marks": subject_total_marks,
            "obtained_marks": subject_obtained_marks,
            "percentage": percentage,
            "grade": grade,
            "remarks": remarks,
            "is_pass": subject_is_pass,
            "is_optional": is_optional
        })

        # Update totals
        total_marks += subject_total_marks
        obtained_marks += subject_obtained_marks if subject_is_pass else 0

    # Update the instance fields
    self.total_marks = total_marks
    self.obtained_marks = obtained_marks
    self.is_pass = is_pass
    self.fail_sub = fail_count
    self.subjects_details = subjects_details

    # Calculate the GPA for the overall result
    percentage = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
    grading_rules = Graderule.objects.all()
    for rule in grading_rules:
        if rule.min_mark <= percentage <= rule.max_mark:
            self.gpa = rule.gpa
            self.remarks = rule.remarks
            break

    return self.gpa  # Return GPA to ensure usage in tests or debugging

def save(self, *args, **kwargs):
    """
    Save the student result and calculate the result before saving.
    """
    self.calculate_result()
    super().save(*args, **kwargs)

from django.core.paginator import Paginator
def calculate_gpa(obtained_marks, total_marks):
    """
    Calculate GPA based on obtained marks and grading rules.
    """
    if total_marks == 0:
        return 0.0

    percentage = (obtained_marks / total_marks) * 100
    grading_rules = Graderule.objects.all().order_by('-min_mark')

    for rule in grading_rules:
        if rule.min_mark <= percentage <= rule.max_mark:
            return rule.gpa

    return 0.0

def paginated_report(request):
    """
    Generate a paginated report for a selected class, section, and exam.
    """
    # Fetch classes, sections, and exams for dropdowns
    classes = StudentClass.objects.all()
    exams = Examname.objects.all()

    class_id = request.GET.get("class_id") or request.POST.get("class_id")
    exam_id = request.GET.get("exam_id") or request.POST.get("exam_id")

    results = StudentResult.objects.none()  # Default to empty queryset

    if class_id and exam_id:
        # Fetch student results for the selected filters
        results = StudentResult.objects.filter(
            student__class_id=class_id,
            exam_id=exam_id
        ).order_by('-obtained_marks')

        # ✅ GPA Calculation Logic (Using Grading Rules)
        grading_rules = [
            {"min_mark": 80, "max_mark": 100, "gpa": 5},
            {"min_mark": 70, "max_mark": 79, "gpa": 4},
            {"min_mark": 60, "max_mark": 69, "gpa": 3.5},
            {"min_mark": 50, "max_mark": 59, "gpa": 3},
            {"min_mark": 40, "max_mark": 49, "gpa": 2},
            {"min_mark": 33, "max_mark": 39, "gpa": 1},
            {"min_mark": 0, "max_mark": 32, "gpa": 0},
        ]

        def get_gpa(marks):
            """Convert marks to GPA based on grading rules"""
            for rule in grading_rules:
                if rule["min_mark"] <= marks <= rule["max_mark"]:
                    return rule["gpa"]
            return 0  

        for result in results:
            subject_marks = Subject_mark.objects.filter(
                student_id=result.student,
                examname_id=exam_id
            )

            total_gp = 0.0
            compulsory_subjects_count = 0
            optional_subject_gp = None

            for mark in subject_marks:
                subject_name = mark.mark_id.subject_conf_id.subject_id.name
                gpa = get_gpa(mark.mark)  # Convert subject marks to GPA
                
                # ✅ Check if the subject is optional
                subject_config = SubjectConfig.objects.filter(subject_id__name=subject_name).first()
                if subject_config and subject_config.subject_type == "CHOOSABLE":
                    optional_subject_gp = gpa  # Store optional subject GPA separately
                else:
                    total_gp += gpa
                    compulsory_subjects_count += 1

            # ✅ Apply 4th Subject Rule: If above 2, add only the extra GP
            if optional_subject_gp and optional_subject_gp > 2:
                total_gp += (optional_subject_gp - 2)

            # ✅ Store computed values in result object
            result.total_gp = round(total_gp, 2)
            result.gpa = round(total_gp / compulsory_subjects_count if compulsory_subjects_count > 0 else 0, 2)

        # Paginate the results (20 per page)
        paginator = Paginator(results, 5)
        page_number = request.GET.get('page', 1)
        paginated_results = paginator.get_page(page_number)

        # Assign positions based on page slicing
        for index, result in enumerate(paginated_results, start=(paginated_results.start_index())):
            result.position = index + 1  # Adjusted position numbering

    else:
        paginated_results = None  # No results to display

    context = {
        "classes": classes,
        "exams": exams,
        "results": paginated_results,
        "class_id": class_id,
        "exam_id": exam_id,
    }

    return render(request, "exams/mark/paginated_report.html", context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, "teacher", roles=['Manager', 'HR', 'DataEntry']))
def subject_wise_analysis(request):
    """Generates subject-wise analysis based on class, section, and exam selection."""
    classes = StudentClass.objects.all()
    sections = StudentSection.objects.all()
    exams = Examname.objects.all()
    results = None

    # Define grading rules
    grading_rules = [
        {"min_mark": 80, "max_mark": 100, "letter": "A_plus"},
        {"min_mark": 70, "max_mark": 79, "letter": "A"},
        {"min_mark": 60, "max_mark": 69, "letter": "A_minus"},
        {"min_mark": 50, "max_mark": 59, "letter": "B"},
        {"min_mark": 40, "max_mark": 49, "letter": "C"},
        {"min_mark": 33, "max_mark": 39, "letter": "D"},
        {"min_mark": 0, "max_mark": 32, "letter": "F"},
    ]

    def get_grade(total_marks):
        """Determine grade based on total marks"""
        for rule in grading_rules:
            if rule["min_mark"] <= total_marks <= rule["max_mark"]:
                return rule["letter"]
        return "F"

    if request.method == "POST":
        selected_class_id = request.POST.get("class_id")
        selected_exam_id = request.POST.get("exam_id")

        if selected_class_id  and selected_exam_id:
            students = StudentProfile.objects.filter(
                class_id=selected_class_id
            )

            subject_marks = Subject_mark.objects.filter(
                student_id__in=students,
                examname_id=selected_exam_id
            ).values(
                "student_id",
                "mark_id__subject_conf_id__subject_id__name"
            ).annotate(
                total_marks=Sum("mark")  # Summing all divided marks (MCQ, CQ, Practical)
            )

            grade_counts = {}
            student_subject_totals = {}

            for entry in subject_marks:
                subject_name = entry["mark_id__subject_conf_id__subject_id__name"]
                student_id = entry["student_id"]
                total_marks = entry["total_marks"]

                # Store the total marks per student per subject
                if subject_name not in student_subject_totals:
                    student_subject_totals[subject_name] = {}
                student_subject_totals[subject_name][student_id] = total_marks

            # Process grades for each subject
            for subject_name, student_marks in student_subject_totals.items():
                if subject_name not in grade_counts:
                    grade_counts[subject_name] = {g["letter"]: 0 for g in grading_rules}

                for student_id, total_marks in student_marks.items():
                    grade = get_grade(total_marks)
                    grade_counts[subject_name][grade] += 1

            # Preparing results with proper dictionary format
            results = []
            for subject, grades in grade_counts.items():
                result_entry = {
                    "subject_name": subject,
                    "total_students": len(student_subject_totals[subject]),  # Unique student count per subject
                }
                result_entry.update(grades)  # Add grade counts dynamically
                results.append(result_entry)

    context = {
        "classes": classes,
        "sections": sections,
        "exams": exams,
        "results": results,
        "grading_rules": grading_rules,
        'heading': 'Result ',
        'subheading': 'Subject Wise Analysis',
    }
    return render(request, "exams/mark/subject_wise_analysis.html", context)


import io
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, "teacher", roles=['Manager', 'HR', 'DataEntry']))
def download_subject_analysis_pdf(request):
    """Generates and downloads the subject-wise analysis as a PDF."""
    
    # Get selected class, section, and exam
    selected_class_id = request.GET.get("class_id")
    selected_exam_id = request.GET.get("exam_id")

    # ✅ Check if all selections are valid
    if not selected_class_id or  not selected_exam_id:
        return HttpResponse("Missing class, or exam selection.", content_type="text/plain")

    try:
        selected_class = StudentClass.objects.get(id=selected_class_id)
        selected_exam = Examname.objects.get(id=selected_exam_id)
    except (StudentClass.DoesNotExist, Examname.DoesNotExist):
        return HttpResponse("Invalid selection. Please select a valid class, section, and exam.", content_type="text/plain")

    # ✅ Proceed with data processing only if selections are valid
    students = StudentProfile.objects.filter(
        class_id=selected_class_id,
    )

    subject_marks = Subject_mark.objects.filter(
        student_id__in=students,
        examname_id=selected_exam_id
    ).values(
        "student_id",
        "mark_id__subject_conf_id__subject_id__name"
    ).annotate(
        total_marks=Sum("mark")  # Summing all divided marks (MCQ, CQ, Practical)
    )

    # Define grading rules
    grading_rules = [
        {"min_mark": 80, "max_mark": 100, "letter": "A+"},
        {"min_mark": 70, "max_mark": 79, "letter": "A"},
        {"min_mark": 60, "max_mark": 69, "letter": "A-"},
        {"min_mark": 50, "max_mark": 59, "letter": "B"},
        {"min_mark": 40, "max_mark": 49, "letter": "C"},
        {"min_mark": 33, "max_mark": 39, "letter": "D"},
        {"min_mark": 0, "max_mark": 32, "letter": "F"},
    ]

    def get_grade(total_marks):
        """Determine grade based on total marks"""
        for rule in grading_rules:
            if rule["min_mark"] <= total_marks <= rule["max_mark"]:
                return rule["letter"]
        return "F"

    grade_counts = {}
    student_subject_totals = {}

    for entry in subject_marks:
        subject_name = entry["mark_id__subject_conf_id__subject_id__name"]
        student_id = entry["student_id"]
        total_marks = entry["total_marks"]

        if subject_name not in student_subject_totals:
            student_subject_totals[subject_name] = {}
        student_subject_totals[subject_name][student_id] = total_marks

    for subject_name, student_marks in student_subject_totals.items():
        if subject_name not in grade_counts:
            grade_counts[subject_name] = {g["letter"]: 0 for g in grading_rules}

        for student_id, total_marks in student_marks.items():
            grade = get_grade(total_marks)
            grade_counts[subject_name][grade] += 1

    results = []
    for subject, grades in grade_counts.items():
        result_entry = {
            "subject_name": subject,
            "total_students": len(student_subject_totals[subject]),  # Unique student count per subject
        }
        result_entry.update(grades)  # Add grade counts dynamically
        results.append(result_entry)

    context = {
        "results": results,
        "grading_rules": grading_rules,
        "selected_class": selected_class.name,
        "selected_exam": selected_exam.name,
    }

    html_string = render_to_string("exams/mark/subject_analysis_pdf.html", context)

    # ✅ Fix CSS Styles in WeasyPrint
    pdf_file = io.BytesIO()
    pdf = HTML(string=html_string).write_pdf(stylesheets=[CSS(string="""
        @page {
            size: A4;
            margin: 20mm;
        }
        body {
            font-family: Arial, sans-serif;
            color: #333;
        }
        h2 {
            text-align: center;
            background-color: #001f3f;
            color: white;
            padding: 10px;
            border-radius: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #001f3f;
            color: white;
            font-size: 14px;
        }
        tr:nth-child(even) { background-color: #f2f2f2; }
        tr:nth-child(odd) { background-color: #ffffff; }
    """)])
    pdf_file.write(pdf)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=subject_analysis.pdf"

    return response

def top_last_students_report(request):
    """
    Generate a report of the top 10 and last 10 students for a selected class and exam (without section).
    """
    # Fetch classes and exams for the dropdowns
    classes = StudentClass.objects.all()
    exams = Examname.objects.all()
    selected_class_id = None
    selected_exam_id = None
    top_10_students = []
    last_10_students = []

    if request.method == "GET":
        # Get selected class and exam from query parameters
        selected_class_id = request.GET.get("class_id")
        selected_exam_id = request.GET.get("exam_id")

        # Fetch student results for the selected filters
        if selected_class_id and selected_exam_id:
            students_results = StudentResult.objects.filter(
                student__class_id__class_group_id__class_id=selected_class_id,
                exam=selected_exam_id
            ).order_by('-obtained_marks')  # Order by total marks descending

            # Get the top 10 students
            top_10_students = list(students_results[:10])

            # Get the last 10 students (safely)
            last_10_students = list(students_results.order_by('obtained_marks')[:10])

    context = {
        "classes": classes,
        "exams": exams,
        "top_10_students": top_10_students,
        "last_10_students": last_10_students,
        "selected_class_id": selected_class_id,
        "selected_exam_id": selected_exam_id,
        'heading': 'Result ',
        'subheading': 'Top 10 and Last 10',
    }
    return render(request, "exams/mark/top_last_students.html", context)

from django.db.models import F
def subject_wise_fail_report(request):
    """
    Generate a report of students who failed in subjects for a selected class and exam.
    """
    # Fetch classes, sections, and exams for dropdowns
    classes = ClassConfig.objects.all()
    exams = Examname.objects.all()
    results = []
    
    selected_class_id = request.GET.get('class_id')
    selected_exam_id = request.GET.get('exam_id')

    if selected_class_id and selected_exam_id:
        # Fetch students who failed in any subject for the selected class, section, and exam
        failed_subjects = Subject_mark.objects.filter(
            student_id__class_id__id=selected_class_id,
            examname_id=selected_exam_id,
            mark__lt=F('mark_id__pass_mark')  # ✅ Corrected Pass Mark Filtering
        ).select_related('student_id', 'mark_id__subject_conf_id__subject_id')

        # Debugging: Print SQL Query
        print(failed_subjects.query)

        # Group data by student and subjects failed
        student_fail_data = {}
        for entry in failed_subjects:
            student = entry.student_id
            subject_name = entry.mark_id.subject_conf_id.subject_id.name

            if student.id not in student_fail_data:
                student_fail_data[student.id] = {
                    'student_name': student.student_field.name,
                    'roll_no': student.class_id,  # ✅ Using College ID
                    'subjects': []
                }
            student_fail_data[student.id]['subjects'].append(subject_name)

        # Format results for the template
        results = [
            {
                'sn': idx + 1,
                'student_name': data['student_name'],
                'roll_no': data['roll_no'],
                'subjects': ', '.join(data['subjects'])
            }
            for idx, data in enumerate(student_fail_data.values())
        ]

    context = {
        'class_list': classes,
        'exam_list': exams,
        'results': results,
        'selected_class_id': selected_class_id,
        'selected_exam_id': selected_exam_id,
        'heading': 'Result ',
        'subheading': 'Subject-Wise Fail Report',
    }
    return render(request, "exams/mark/subject_wise_fail_report.html", context)

# def tabulation_sheet_two(request):
#     # Fetch classes and exams for dropdowns
#     classes = StudentClass.objects.all()
#     sections = StudentSection.objects.all()
#     exams = Examname.objects.all()

#     # Get filters from the form
#     selected_class_id = request.POST.get("class_id")
#     selected_section_id = request.POST.get("section_id")
#     selected_exam_id = request.POST.get("exam_id")

#     tabulation_data = []

#     if selected_class_id and selected_section_id and selected_exam_id:
#         # Fetch students for the selected class and section
#         students = StudentProfile.objects.filter(
#             class_id__class_group_id__class_id=selected_class_id,
#             class_id__section_id=selected_section_id,
#         )

#         for student in students:
#             student_data = {
#                 "roll": student.id,
#                 "name": student.student_field.name,
#                 "stream": student.class_id.class_group_id.group_id.name,
#                 "section": student.class_id.section_id.name,
#                 "subjects": {},
#                 "total_marks": 0,
#                 "gpa": 0,
#             }

#             # Fetch marks for the selected student and exam
#             marks = Subject_mark.objects.filter(
#                 student_id=student.id,
#                 examname_id=selected_exam_id,
#             ).select_related("mark_id__subject_conf_id__subject_id", "mark_id__mark_type_id")

#             total_gpa = 0
#             fail_flag = False

#             # Organize marks by subject
#             for mark in marks:
#                 subject_name = mark.mark_id.subject_conf_id.subject_id.name
#                 mark_type_name = mark.mark_id.mark_type_id.name
#                 obtained_marks = mark.mark

#                 if subject_name not in student_data["subjects"]:
#                     student_data["subjects"][subject_name] = {
#                         "marks": {},
#                         "total": 0,
#                         "grade": None,
#                         "gpa": 0,
#                     }

#                 student_data["subjects"][subject_name]["marks"][mark_type_name] = obtained_marks
#                 student_data["subjects"][subject_name]["total"] += obtained_marks

#                 # Calculate grade and GPA
#                 grading = Graderule.objects.filter(
#                     min_mark__lte=obtained_marks,
#                     max_mark__gte=obtained_marks,
#                 ).first()

#                 if grading:
#                     student_data["subjects"][subject_name]["grade"] = grading.grade_name
#                     student_data["subjects"][subject_name]["gpa"] = grading.gpa
#                     total_gpa += grading.gpa
#                 else:
#                     fail_flag = True

#             # Add total marks and GPA
#             student_data["total_marks"] = sum(
#                 [subject["total"] for subject in student_data["subjects"].values()]
#             )
#             student_data["gpa"] = round(total_gpa / len(student_data["subjects"]), 2) if student_data["subjects"] else 0
#             student_data["status"] = "Fail" if fail_flag else "Pass"

#             tabulation_data.append(student_data)

#     context = {
#         "classes": classes,
#         "sections": sections,
#         "exams": exams,
#         "tabulation_data": tabulation_data,
#         "selected_class_id": selected_class_id,
#         "selected_section_id": selected_section_id,
#         "selected_exam_id": selected_exam_id,
#     }

#     return render(request, "exams/mark/tabulation_sheet_two.html", context)

def get_grade(percentage):
    """Returns GPA and Grade based on percentage"""
    grading = Graderule.objects.filter(
        min_mark__lte=percentage,
        max_mark__gte=percentage
    ).first()

    if grading:
        return grading.gpa, grading.grade_name
    return 0.00, "F"

def tabulation_sheet_two(request):
    # Fetch classes, sections, and exams for dropdowns
    classes = ClassConfig.objects.all()
    exams = Examname.objects.all()

    selected_class_id = request.POST.get("class_id")
    selected_exam_id = request.POST.get("exam_id")

    tabulation_data = []

    if selected_class_id  and selected_exam_id:
        # Fetch students in the selected class and section
        students = StudentProfile.objects.filter(
            class_id=selected_class_id
        )

        for student in students:
            student_data = {
                "roll": student.id,
                "name": student.student_field.name,
                "stream": student.class_id.class_group_id.group_id.name if student.class_id.class_group_id.group_id else None,
                "section": student.class_id.section_id.name if student.class_id.section_id else None,
                "subjects": {},
                "total_marks": 0,
                "total_gpa": 0,
                "final_grade": None,
                "status": "Pass",
            }

            # Fetch all subjects assigned to the class
            subjects = SubjectConfig.objects.filter(class_id=student.class_id.class_group_id)

            total_gpa_sum = 0
            total_gpa_count = 0
            total_marks_obtained = 0
            total_marks_possible = 0

            for subject in subjects:
                subject_name = subject.subject_id.name
                student_data["subjects"][subject_name] = {"marks": {}, "total": 0, "gpa": 0, "grade": None}

                # Fetch the max possible marks from `Mark_config`
                mark_configs = Mark_config.objects.filter(
                    class_id=student.class_id.class_group_id,
                    subject_conf_id=subject
                )

                max_marks = sum(mark_config.mark for mark_config in mark_configs)
                total_marks_possible += max_marks

                # Fetch the student's marks for the subject
                marks = Subject_mark.objects.filter(
                    student_id=student.id,
                    examname_id=selected_exam_id,
                    mark_id__subject_conf_id=subject
                ).select_related("mark_id__mark_type_id")

                total_marks = 0

                for mark in marks:
                    mark_type_name = mark.mark_id.mark_type_id.name
                    obtained_marks = mark.mark

                    student_data["subjects"][subject_name]["marks"][mark_type_name] = obtained_marks
                    total_marks += obtained_marks

                # Calculate percentage and determine grade & GPA
                percentage = (total_marks / max_marks) * 100 if max_marks > 0 else 0
                gpa, grade = get_grade(percentage)

                student_data["subjects"][subject_name]["total"] = total_marks
                student_data["subjects"][subject_name]["gpa"] = gpa
                student_data["subjects"][subject_name]["grade"] = grade

                # Update totals for final GPA and grade calculation
                total_marks_obtained += total_marks
                total_gpa_sum += gpa
                total_gpa_count += 1 if max_marks > 0 else 0

            # Calculate final GPA and Grade
            student_data["total_marks"] = total_marks_obtained
            student_data["total_gpa"] = round(total_gpa_sum / total_gpa_count, 2) if total_gpa_count > 0 else 0

            final_percentage = (total_marks_obtained / total_marks_possible) * 100 if total_marks_possible > 0 else 0
            student_data["final_grade"] = get_grade(final_percentage)[1]

            tabulation_data.append(student_data)

    context = {
        "classes": classes,
        "exams": exams,
        "tabulation_data": tabulation_data,
        "selected_class_id": selected_class_id,
        "selected_exam_id": selected_exam_id,
        'heading': 'Result ',
        'subheading': 'Tabulation Sheet',
    }

    return render(request, "exams/mark/tabulation_sheet_two.html", context)

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

def tabulation_pdf(request):
    """Generates a compressed PDF for the tabulation sheet in landscape format"""

    selected_class_id = request.GET.get("class_id")
    selected_section_id = request.GET.get("section_id")
    selected_exam_id = request.GET.get("exam_id")

    # Fetch student data
    students = StudentProfile.objects.filter(
        class_id__class_group_id__class_id=selected_class_id,
        class_id__section_id=selected_section_id
    )

    tabulation_data = []
    subject_list = set()  # Store all unique subjects

    for student in students:
        student_data = {
            "roll": student.id,
            "name": student.student_field.name,
            "stream": student.class_id.class_group_id.group_id.name if student.class_id.class_group_id.group_id else None,
            "section": student.class_id.section_id.name if student.class_id.section_id else None,
            "subjects": {},
            "total_marks": 0,
            "total_gpa": 0,
            "status": "Pass",
        }

        subjects = SubjectConfig.objects.filter(class_id=student.class_id.class_group_id)

        total_marks_obtained = 0

        for subject in subjects:
            subject_name = subject.subject_id.name
            subject_list.add(subject_name)  # Add to unique subject set
            student_data["subjects"][subject_name] = {"marks": {}, "total": 0}

            marks = Subject_mark.objects.filter(
                student_id=student.id,
                examname_id=selected_exam_id,
                mark_id__subject_conf_id=subject
            ).select_related("mark_id__mark_type_id")

            total_marks = 0

            for mark in marks:
                mark_type_name = mark.mark_id.mark_type_id.name.upper()
                obtained_marks = mark.mark
                student_data["subjects"][subject_name]["marks"][mark_type_name] = obtained_marks
                total_marks += obtained_marks

            student_data["subjects"][subject_name]["total"] = total_marks
            total_marks_obtained += total_marks

        student_data["total_marks"] = total_marks_obtained
        tabulation_data.append(student_data)

    # **DYNAMIC FONT SIZE & COLUMN WIDTH**
    subject_count = len(subject_list)
    base_font_size = max(5, 10 - (subject_count // 4))  # Reduce font dynamically
    base_padding = max(2, 6 - (subject_count // 4))  # Reduce padding
    column_width = 100 / (4 + (subject_count * 3) + 3)  # Adjust width

    context = {
        "tabulation_data": tabulation_data,
        "subject_list": sorted(subject_list),
        "column_width": column_width,
        "font_size": base_font_size,
        "padding": base_padding,
    }

    # Convert HTML to PDF
    html_string = render_to_string("exams/mark/tabulation_pdf_template.html", context)
    pdf_file = HTML(string=html_string).write_pdf(
        stylesheets=[CSS(string=f"""
            @page {{
                size: A4 landscape;
                margin: 5px;
            }}
            table {{
                table-layout: fixed;
                width: 100%;
            }}
            th, td {{
                font-size: {base_font_size}px;
                padding: {base_padding}px;
                word-wrap: break-word;
                overflow: hidden;
            }}
        """)]
    )

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=tabulation_sheet.pdf"
    return response





def generate_admit_cards(request):
    classList = ClassConfig.objects.all()
    examList = Examname.objects.all()
    institute = Institute.objects.latest('updated_at')

    if request.method == 'POST':
        try:
            class_id = request.POST.get('class_name_id')
            exam_id = request.POST.get('exam_name_id')

            # Get active students with paid fees
            students = StudentProfile.objects.filter(
                class_id=class_id,
                status='Active'
            ).select_related('student_field', 'class_id__class_group_id')

            # Filter only students with paid fees
            paid_students = []
            for student in students:
                # Check if student has any unpaid fees for the current academic year
                has_unpaid_fees = Fees.objects.filter(
                    student_id=student,
                    status__in=['unpaid', 'partial']
                ).exists()
                
                if not has_unpaid_fees:
                    paid_students.append(student)

            if not paid_students:
                return HttpResponse("No eligible students found (must be active and have paid all fees).")

            exam_instance = get_object_or_404(Examname, id=exam_id)
            
            # Prepare student data with avatar URLs
            for student in paid_students:
                if student.student_field and student.student_field.avatar:
                    student.avatar_url = request.build_absolute_uri(student.student_field.avatar.url)
                else:
                    student.avatar_url = None

            ins_logo = request.build_absolute_uri(institute.institute_logo.url) if institute.institute_logo else None
            
            # Group students into sets of 3 for the PDF layout
            student_groups = [paid_students[i:i + 3] for i in range(0, len(paid_students), 3)]
            
            html_string = render_to_string('admit_card_pdf_template.html', {
                'student_groups': student_groups,
                'ins_logo': ins_logo,
                'exam_instance': exam_instance,
                'institute': institute
            })
            
            pdf_file = HTML(string=html_string).write_pdf()
            
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="admit_cards.pdf"'
            
            return response
        except Exception as e:
            print(f"Error: {e}")
            return HttpResponse("An error occurred while generating the admit cards.")
        
    context = {
        'classList': classList,
        'examList': examList,
        'heading': 'Exam',
        'subheading': 'Admit Card Download',
    }
    return render(request, 'layout/admit_card_download_form.html', context)