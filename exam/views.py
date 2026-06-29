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

"""
==========================================================================
 REPLACEMENT for progress_report (exam/views.py)
 + NEW: progress_report_pdf
==========================================================================
 Purono `progress_report` function REPLACE korun ei version diye.
 progress_report_pdf NOTUN function — niche add korun.

 KI UPGRADE HOLO (reference transcript er moto):
  - Institute header (dynamic: name/address/eiin/logo) — Institute model theke
  - Protita subject e mark-type breakdown (Subjective/Objective/etc),
    subject total, full marks, GP, LG (letter) — sob ekoshathe
  - Total marks, final GPA, letter grade, Position in class
  - Roll/Name/Section/Shift/Version header grid
  - Ekhono optional (4th subject) GPA logic thik ache
  - UI te ja dekhbe PDF teo tai (ek shared builder)
  - Position auto-calculate (total marks onujayi rank)

 NOTE: get_grade niche-i define kora ache (independent), tai onno
 get_grade er sathe conflict nei.
==========================================================================
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS


def _pr_get_grade(value, mode="marks"):
    if mode == "gpa":
        rules = [
            (5.00, 5.00, None, "A+"), (4.00, 4.99, None, "A"),
            (3.50, 3.99, None, "A-"), (3.00, 3.49, None, "B"),
            (2.00, 2.99, None, "C"), (1.00, 1.99, None, "D"),
            (0.00, 0.99, None, "F"),
        ]
    else:
        rules = [
            (80, 100, 5, "A+"), (70, 79, 4, "A"), (60, 69, 3.5, "A-"),
            (50, 59, 3, "B"), (40, 49, 2, "C"), (33, 39, 1, "D"),
            (0, 32, 0, "F"),
        ]
    for lo, hi, gp, lg in rules:
        if lo <= value <= hi:
            return (gp if gp is not None else 0), lg
    return 0, "F"


def _build_progress(exam_instance, class_instance, admission_year):
    """
    UI ar PDF — duitoই ei builder use kore.
    Returns: (results, mark_type_list)
    results = list of student dict with full breakdown.
    """
    class_group_instance = class_instance.class_group_id
    students = StudentProfile.objects.filter(
        Q(class_id=class_instance.id)
        & Q(admission_year_id=admission_year)
        & Q(student_field__status="Active")
    ).select_related('student_field', 'class_id', 'class_id__section_id',
                     'class_id__shift_id').order_by("roll_no")

    mark_type_list = []   # global order of mark types (CQ/MCQ/etc)
    results = []

    for student in students:
        compulsory = SubjectConfig.objects.filter(
            class_id=class_group_instance, subject_type='COMPULSARY'
        ).select_related('subject_id').order_by('subject_Serial')
        optional_qs = Forth_Sub.objects.filter(student_id=student, forth_type="OPTIONAL")
        optional_conf_ids = set(optional_qs.values_list('sub_conf_id', flat=True))
        all_subjects = list(compulsory) + [o.sub_conf_id for o in optional_qs]

        subjects_data = []
        total_marks = 0
        total_gpa_without_optional = 0
        compulsory_count = 0
        optional_gpa = 0

        for subject in all_subjects:
            is_optional = subject.id in optional_conf_ids

            sm = Subject_mark.objects.filter(
                student_id=student, examname_id=exam_instance,
                mark_id__subject_conf_id=subject
            ).select_related('mark_id__mark_type_id')

            marks_by_type = {}
            subj_total = 0
            for m in sm:
                if not m.mark_id:
                    continue
                mt = m.mark_id.mark_type_id.name.upper()
                if mt not in mark_type_list:
                    mark_type_list.append(mt)
                val = round(m.mark or 0, 2)
                marks_by_type[mt] = val
                subj_total += val

            subj_total = round(subj_total, 2)
            full_marks = subject.mark if subject.mark is not None else 100
            percentage = (subj_total / full_marks) * 100 if full_marks > 0 else 0
            gp, lg = _pr_get_grade(percentage)

            subjects_data.append({
                "name": subject.subject_id.name if subject.subject_id else "Unknown",
                "marks": marks_by_type,
                "total": subj_total,
                "full_marks": full_marks,
                "gp": gp,
                "lg": lg,
                "is_optional": is_optional,
            })

            total_marks += subj_total
            if is_optional:
                optional_gpa = max(optional_gpa, gp)
            else:
                total_gpa_without_optional += gp
                compulsory_count += 1

        total_with_optional = total_gpa_without_optional + max(0, optional_gpa - 2)
        final_gpa = round(total_with_optional / compulsory_count, 2) if compulsory_count else 0
        final_letter = _pr_get_grade(final_gpa, mode="gpa")[1]

        results.append({
            "student": student,
            "name": student.student_field.name,
            "roll_no": student.roll_no if student.roll_no is not None else "-",
            "section": student.class_id.section_id.name if student.class_id.section_id else "",
            "shift": student.class_id.shift_id.name if student.class_id.shift_id else "",
            "version": student.version,
            "subjects": subjects_data,
            "total_marks": round(total_marks, 2),
            "gpa": final_gpa,
            "grade": final_letter,
            "position": None,   # niche fill kora hobe
        })

    # Position (class rank) — total marks onujayi
    ranked = sorted(results, key=lambda r: r["total_marks"], reverse=True)
    for idx, r in enumerate(ranked, start=1):
        r["position"] = idx

    # Highest mark per subject (whole class) — reference er moto
    highest = {}
    for r in results:
        for sub in r["subjects"]:
            nm = sub["name"]
            if nm not in highest or sub["total"] > highest[nm]:
                highest[nm] = sub["total"]
    for r in results:
        for sub in r["subjects"]:
            sub["highest"] = highest.get(sub["name"], sub["total"])

    return results, mark_type_list


def progress_report(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    exam_list = Examname.objects.filter(academic_year=admission_year)
    class_list = ClassConfig.objects.all()

    context = {
        'exam_list': exam_list,
        'class_list': class_list,
        'heading': 'Result',
        'subheading': 'Progress Report',
    }

    if request.method == "POST":
        exam_id = request.POST.get('exam_name_id')
        class_id = request.POST.get('class_name_id')
        exam_instance = get_object_or_404(Examname, pk=exam_id)
        class_instance = get_object_or_404(ClassConfig, pk=class_id)

        results, mark_type_list = _build_progress(
            exam_instance, class_instance, admission_year
        )
        context.update({
            'exam_instance': exam_instance,
            'class_instance': class_instance,
            'institute': Institute.objects.first(),
            'results': results,
            'mark_type_list': mark_type_list,
            'selected_exam_id': exam_id,
            'selected_class_id': class_id,
        })

    return render(request, 'exams/mark/progress_report.html', context)


def progress_report_pdf(request):
    """Reference-style PDF — ek student per page."""
    admission_year = Admission_Year.objects.latest('updated_at')
    exam_id = request.GET.get('exam_id')
    class_id = request.GET.get('class_id')
    exam_instance = get_object_or_404(Examname, pk=exam_id)
    class_instance = get_object_or_404(ClassConfig, pk=class_id)

    results, mark_type_list = _build_progress(
        exam_instance, class_instance, admission_year
    )

    cg = class_instance.class_group_id
    context = {
        'institute': Institute.objects.first(),
        'exam_instance': exam_instance,
        'class_instance': class_instance,
        'class_name': cg.class_id.name if cg and cg.class_id else "",
        'group_name': cg.group_id.name if cg and cg.group_id else "",
        'academic_year': admission_year.name if admission_year else "",
        'results': results,
        'mark_type_list': mark_type_list,
    }

    html_string = render_to_string('exams/mark/progress_report_pdf.html', context)
    pdf_file = HTML(
        string=html_string, base_url=request.build_absolute_uri('/')
    ).write_pdf(stylesheets=[CSS(string="@page { size: A4 portrait; margin: 10mm; }")])

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=progress_report.pdf"
    return response

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


"""
=========================================================================
 REPLACEMENT for download_result_report_pdf (exam/views.py)
=========================================================================
 KENO PURONO TA BHUL CHILO:
  1. Subject-wise Failed: purono PDF e Count('id', mark__lt=33) - eta
     protita mark ROW (CQ/MCQ/Practical alada) gunto, tai Bangla=5,
     ICT=10 erom bhul. EKHON UI er moto subject TOTAL diye fail gona hoy.
  2. GPA Distribution: purono PDF e bucket gulo (4.5_and_above...) UI er
     theke ALADA chilo, tai count milto na. EKHON UI er moto EKOI bucket.
  3. Color: navy #2A3F54 -> teal.
  4. Institute name/address PDF e add kora holo.

 EKHON UI ar PDF EKOI logic use kore (download er data UI er sathe mile).
=========================================================================
"""

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Sum, F, Q
from weasyprint import HTML, CSS


def download_result_report_pdf(request):
    selected_class_id = request.GET.get("class_id")
    selected_exam_id = request.GET.get("exam_id")

    if not selected_class_id or not selected_exam_id:
        return HttpResponseBadRequest("Error: Missing class_id or exam_id parameters.")

    try:
        selected_class_id = int(selected_class_id)
        selected_exam_id = int(selected_exam_id)
    except ValueError:
        return HttpResponseBadRequest("Error: Invalid class_id or exam_id format.")

    exam = get_object_or_404(Examname, id=selected_exam_id)
    students = StudentProfile.objects.filter(class_id=selected_class_id)

    if not students.exists():
        return HttpResponseBadRequest("Error: No students found for the selected criteria.")

    # ---- Subject-wise marks aggregate (UI er moto) ----
    subject_marks = Subject_mark.objects.filter(
        student_id__in=students, examname_id=exam
    ).values(
        'student_id',
        'mark_id__subject_conf_id__subject_id__name'
    ).annotate(
        total_marks=Sum('mark'),
        max_marks=Sum(F('mark_id__mark')),
        min_pass=Sum(F('mark_id__pass_mark')),
    )

    # Subject-wise FAILED — subject TOTAL diye (NOT per-row)
    subject_fail_counts = {}
    for mark in subject_marks:
        subject_name = mark['mark_id__subject_conf_id__subject_id__name']
        total = mark['total_marks'] or 0
        max_m = mark['max_marks'] or 0
        min_pass = mark['min_pass'] or 0
        percentage = (total / max_m) * 100 if max_m else 0
        failed = percentage < 33 or total < min_pass
        subject_fail_counts.setdefault(subject_name, 0)
        if failed:
            subject_fail_counts[subject_name] += 1

    # ---- StudentResult based stats (UI er moto) ----
    student_results = StudentResult.objects.filter(student__in=students, exam=exam)

    gpa_data = {
        "gpa_5": student_results.filter(gpa=5.00).count(),
        "gpa_4_to_4_99": student_results.filter(gpa__gte=4.00, gpa__lt=5.00).count(),
        "gpa_3_5_to_3_99": student_results.filter(gpa__gte=3.50, gpa__lt=4.00).count(),
        "gpa_3_to_3_49": student_results.filter(gpa__gte=3.00, gpa__lt=3.50).count(),
        "gpa_2_to_2_99": student_results.filter(gpa__gte=2.00, gpa__lt=3.00).count(),
        "gpa_1_to_1_99": student_results.filter(gpa__gte=1.00, gpa__lt=2.00).count(),
        "gpa_below_1": student_results.filter(gpa__lt=1.00).count(),
    }

    obtained = [m for m in student_results.values_list('obtained_marks', flat=True) if m is not None]
    highest_marks = max(obtained) if obtained else 0
    lowest_marks = min(obtained) if obtained else 0

    total_students = students.count()
    passed_students = student_results.filter(is_pass=True).count()
    failed_students = student_results.filter(is_pass=False).count()
    absent_students = Subject_mark.objects.filter(
        student_id__in=students, examname_id=exam, check_mark=False
    ).values('student_id').distinct().count()

    context = {
        "institute": Institute.objects.first(),
        "exam_name": exam.name,
        "total_students": total_students,
        "passed_students": passed_students,
        "failed_students": failed_students,
        "absent_students": absent_students,
        "gpa_data": gpa_data,
        "highest_marks": highest_marks,
        "lowest_marks": lowest_marks,
        "subject_wise_data": subject_fail_counts,   # dict: subject -> fail count
    }

    html_string = render_to_string("exams/mark/result_report_pdf.html", context)
    pdf_file = HTML(
        string=html_string, base_url=request.build_absolute_uri('/')
    ).write_pdf(stylesheets=[CSS(string="@page { size: A4 portrait; margin: 12mm; }")])

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
grading_rules = [
    {"min_mark": 80, "max_mark": 100, "letter": "A+"},
    {"min_mark": 70, "max_mark": 79, "letter": "A"},
    {"min_mark": 60, "max_mark": 69, "letter": "A-"},
    {"min_mark": 50, "max_mark": 59, "letter": "B"},
    {"min_mark": 40, "max_mark": 49, "letter": "C"},
    {"min_mark": 33, "max_mark": 39, "letter": "D"},
    {"min_mark": 0, "max_mark": 32, "letter": "F"},
]
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
        "selected_class_id": request.POST.get("class_id"),
        "selected_exam_id": request.POST.get("exam_id"),
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

    selected_class_id = request.GET.get("class_id")
    selected_exam_id = request.GET.get("exam_id")

    if not selected_class_id or not selected_exam_id:
        return HttpResponse("Missing class, or exam selection.", content_type="text/plain")

    try:
        selected_class = StudentClass.objects.get(id=selected_class_id)
        selected_exam = Examname.objects.get(id=selected_exam_id)
    except (StudentClass.DoesNotExist, Examname.DoesNotExist):
        return HttpResponse("Invalid selection. Please select a valid class and exam.", content_type="text/plain")

    students = StudentProfile.objects.filter(class_id=selected_class_id)

    subject_marks = Subject_mark.objects.filter(
        student_id__in=students,
        examname_id=selected_exam_id
    ).values(
        "student_id",
        "mark_id__subject_conf_id__subject_id__name"
    ).annotate(
        total_marks=Sum("mark")
    )

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
            "total_students": len(student_subject_totals[subject]),
        }
        result_entry.update(grades)
        results.append(result_entry)

    context = {
        "results": results,
        "grading_rules": grading_rules,
        "selected_class": selected_class.name,
        "selected_exam": selected_exam.name,
        "institute": Institute.objects.first(),
    }

    html_string = render_to_string("exams/mark/subject_analysis_pdf.html", context)

    pdf = HTML(string=html_string).write_pdf(
        stylesheets=[CSS(string="@page { size: A4; margin: 14mm; }")]
    )

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=subject_analysis.pdf"
    return response

"""
=========================================================================
 REPLACEMENT for top_last_students_report (exam/views.py)
 + NEW: download_top_last_pdf
=========================================================================
 KI THIK HOLO:
  - Total student joto, tar besi "Top 10" dekhabe na (4 jon thakle 4-i).
  - Last 10 ekhon NICHER dik theke (boro->choto kore dekhano, ulta
    crom na). Top ar Last e jodi student kom thake tahole overlap
    ekhono thakte pare (eta normal — kom student thakle), kintu ekhon
    Last list ta nicher 10 jon (sorted boro->choto).
  - rank, total marks (2 decimal), GPA (2 decimal) — sob clean.
  - PDF download jukto.

 NOTE: rank list er moddhei thake (top: 1..N; last: nicher der rank).
=========================================================================
"""

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML, CSS


def _round2(v):
    try:
        return round(float(v), 2)
    except (TypeError, ValueError):
        return 0


def _top_last_data(selected_class_id, selected_exam_id, limit=10):
    """UI ar PDF duitoই use kore. Returns (top_list, last_list, total)."""
    qs = StudentResult.objects.filter(
        student__class_id__class_group_id__class_id=selected_class_id,
        exam=selected_exam_id
    ).select_related('student__student_field').order_by('-obtained_marks')

    total = qs.count()

    def pack(results, start_rank):
        out = []
        for i, r in enumerate(results, start=start_rank):
            sf = r.student.student_field if r.student else None
            out.append({
                "rank": i,
                "name": sf.name if sf else "-",
                "college_id": getattr(sf, "college_id", "") or "-",
                "total_marks": _round2(r.obtained_marks),
                "gpa": _round2(r.gpa),
            })
        return out

    # Top: highest first, rank 1..
    top_list = pack(list(qs[:limit]), 1)

    # Last: nicher limit jon, kintu boro->choto kore dekhabo.
    # Tader actual rank = (total - count_in_last + 1) ... total
    last_qs = list(qs.order_by('obtained_marks')[:limit])  # choto->boro
    last_qs = list(reversed(last_qs))                       # boro->choto
    last_start_rank = total - len(last_qs) + 1
    last_list = pack(last_qs, last_start_rank)

    return top_list, last_list, total


def top_last_students_report(request):
    classes = StudentClass.objects.all()
    exams = Examname.objects.all()
    selected_class_id = request.GET.get("class_id")
    selected_exam_id = request.GET.get("exam_id")
    top_10_students = []
    last_10_students = []
    total_students = 0

    if selected_class_id and selected_exam_id:
        top_10_students, last_10_students, total_students = _top_last_data(
            selected_class_id, selected_exam_id
        )

    context = {
        "classes": classes,
        "exams": exams,
        "top_10_students": top_10_students,
        "last_10_students": last_10_students,
        "total_students": total_students,
        "selected_class_id": selected_class_id,
        "selected_exam_id": selected_exam_id,
        'heading': 'Result ',
        'subheading': 'Top 10 and Last 10',
    }
    return render(request, "exams/mark/top_last_students.html", context)


def download_top_last_pdf(request):
    selected_class_id = request.GET.get("class_id")
    selected_exam_id = request.GET.get("exam_id")

    if not selected_class_id or not selected_exam_id:
        return HttpResponseBadRequest("Error: Missing class_id or exam_id.")

    exam = get_object_or_404(Examname, id=selected_exam_id)
    try:
        selected_class = StudentClass.objects.get(id=selected_class_id)
        class_name = selected_class.name
    except StudentClass.DoesNotExist:
        class_name = ""

    top_list, last_list, total = _top_last_data(selected_class_id, selected_exam_id)

    context = {
        "institute": Institute.objects.first(),
        "exam_name": exam.name,
        "class_name": class_name,
        "total_students": total,
        "top_10_students": top_list,
        "last_10_students": last_list,
    }

    html_string = render_to_string("exams/mark/top_last_pdf.html", context)
    pdf_file = HTML(
        string=html_string, base_url=request.build_absolute_uri('/')
    ).write_pdf(stylesheets=[CSS(string="@page { size: A4 portrait; margin: 12mm; }")])

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=top_last_students.pdf"
    return response
"""
=========================================================================
 REPLACEMENT for subject_wise_fail_report (exam/views.py)
 + NEW: download_subject_fail_pdf
=========================================================================
 KI THIK HOLO:
  - roll_no e age VUL kore class_id (pura object) boshano chilo ->
    ekhon ASOL roll_no (student.roll_no).
  - Fail hisab ekhon SUBJECT TOTAL diye (CQ+MCQ+Practical jog kore
    pass_mark er sathe tulona). Age protita row alada dekhto, tai
    ekই subject e ekadhikbar / vul ashto.
  - Failed subjects + koyti subject e fail — dekhano hoy.
  - PDF download (teal, institute header).
=========================================================================
"""

from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML, CSS


def _build_fail_report(selected_class_id, selected_exam_id):
    """UI + PDF — ek builder. Returns results list."""
    # Subject TOTAL (per student per subject) ber kori, sathe pass_mark
    rows = Subject_mark.objects.filter(
        student_id__class_id__id=selected_class_id,
        examname_id=selected_exam_id
    ).values(
        'student_id',
        'student_id__roll_no',
        'student_id__student_field__name',
        'mark_id__subject_conf_id__subject_id__name',
    ).annotate(
        subj_total=Sum('mark'),
        subj_full=Sum(F('mark_id__mark')),
        subj_pass=Sum(F('mark_id__pass_mark')),
    )

    student_fail = {}
    for r in rows:
        total = r['subj_total'] or 0
        full = r['subj_full'] or 0
        passm = r['subj_pass'] or 0
        percentage = (total / full) * 100 if full > 0 else 0
        # Fail jodi: percentage 33% er kom, OR pass_mark set thakle tar kom
        failed = percentage < 33 or (passm > 0 and total < passm)
        if failed:
            sid = r['student_id']
            if sid not in student_fail:
                student_fail[sid] = {
                    'name': r['student_id__student_field__name'],
                    'roll_no': r['student_id__roll_no'] if r['student_id__roll_no'] is not None else '-',
                    'subjects': [],
                }
            student_fail[sid]['subjects'].append(
                r['mark_id__subject_conf_id__subject_id__name']
            )

    results = []
    for idx, data in enumerate(student_fail.values(), start=1):
        results.append({
            'sn': idx,
            'student_name': data['name'],
            'roll_no': data['roll_no'],
            'fail_count': len(data['subjects']),
            'subjects': ', '.join(data['subjects']),
        })
    # roll onujayi sort
    results.sort(key=lambda x: (x['roll_no'] if isinstance(x['roll_no'], int) else 999999))
    for i, r in enumerate(results, start=1):
        r['sn'] = i
    return results


def subject_wise_fail_report(request):
    classes = ClassConfig.objects.all()
    exams = Examname.objects.all()
    results = []
    selected_class_id = request.GET.get('class_id')
    selected_exam_id = request.GET.get('exam_id')

    if selected_class_id and selected_exam_id:
        results = _build_fail_report(selected_class_id, selected_exam_id)

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


def download_subject_fail_pdf(request):
    selected_class_id = request.GET.get('class_id')
    selected_exam_id = request.GET.get('exam_id')

    if not selected_class_id or not selected_exam_id:
        return HttpResponseBadRequest("Error: Missing class_id or exam_id.")

    exam = get_object_or_404(Examname, id=selected_exam_id)
    try:
        class_name = ClassConfig.objects.get(id=selected_class_id).__str__()
    except ClassConfig.DoesNotExist:
        class_name = ""

    results = _build_fail_report(selected_class_id, selected_exam_id)

    context = {
        'institute': Institute.objects.first(),
        'exam_name': exam.name,
        'class_name': class_name,
        'results': results,
    }
    html_string = render_to_string("exams/mark/subject_wise_fail_pdf.html", context)
    pdf_file = HTML(
        string=html_string, base_url=request.build_absolute_uri('/')
    ).write_pdf(stylesheets=[CSS(string="@page { size: A4 portrait; margin: 12mm; }")])

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=subject_wise_fail.pdf"
    return response

def get_grade(percentage):
    """Returns GPA and Grade based on percentage"""
    grading = Graderule.objects.filter(
        min_mark__lte=percentage,
        max_mark__gte=percentage
    ).first()

    if grading:
        return grading.gpa, grading.grade_name
    return 0.00, "F"

"""
==========================================================================
 REPLACEMENT for tabulation_sheet_two + tabulation_pdf  (exam/views.py)
==========================================================================
 Purono duita function (tabulation_sheet_two ar tabulation_pdf) ke ei
 niche deya version diye REPLACE korun. get_grade(percentage) function
 ta jodi age thekei thake (line ~2792), oita rakhun — eta sei tai use kore.

 KI THIK HOLO:
  1. Blank PDF: PDF view e student filter bhul chilo
     (class_id__class_group_id__class_id + section_id). Ekhon duito
     view-i EKOI filter use kore: StudentProfile.filter(class_id=<ClassConfig.id>)
     — tai preview-te ja dekhe PDF-eo thik tai ashe.
  2. Auto-download: template er JS auto-click serano hoyeche (niche template e).
  3. roll: ekhon student.id na, asol roll_no dekhabe.
  4. status: F grade pele "Fail", na hole "Pass" (hardcoded chilo).
  5. GPA + grade duito view-i hisheb kore (PDF-eo GPA thik ashe).
  6. Marks dynamic: MCQ/CQ hardcode na kore je mark_type ache shob dekhabe.
  7. Data validation: max_marks 0 hole divide-by-zero guard ache.
==========================================================================
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS


def _build_tabulation(selected_class_id, selected_exam_id):
    """
    Preview ar PDF — duito-i ei EK helper use kore, tai data shob shomoy
    consistent. Returns (tabulation_data, subject_list, mark_type_list).
    """
    tabulation_data = []
    subject_list = []          # order rakhar jonno list (set noy)
    mark_type_list = []        # je mark type gula ache (MCQ/CQ/Practical...)

    if not (selected_class_id and selected_exam_id):
        return tabulation_data, subject_list, mark_type_list

    students = StudentProfile.objects.filter(
        class_id=selected_class_id
    ).select_related(
        'student_field', 'class_id', 'class_id__class_group_id',
        'class_id__class_group_id__group_id', 'class_id__section_id'
    ).order_by('roll_no')

    for student in students:
        group = student.class_id.class_group_id.group_id
        section = student.class_id.section_id

        student_data = {
            "roll": student.roll_no if student.roll_no is not None else "-",
            "name": student.student_field.name,
            "stream": group.name if group else "",
            "section": section.name if section else "",
            "subjects": {},
            "total_marks": 0,
            "total_gpa": 0,
            "final_grade": None,
            "status": "Pass",
        }

        subjects = SubjectConfig.objects.filter(
            class_id=student.class_id.class_group_id
        ).select_related('subject_id').order_by('subject_Serial')

        total_gpa_sum = 0
        total_gpa_count = 0
        total_marks_obtained = 0
        total_marks_possible = 0
        any_fail = False

        for subject in subjects:
            subject_name = subject.subject_id.name if subject.subject_id else "Unknown"
            if subject_name not in subject_list:
                subject_list.append(subject_name)

            student_data["subjects"][subject_name] = {
                "marks": {}, "total": 0, "gpa": 0, "grade": None
            }

            mark_configs = Mark_config.objects.filter(
                class_id=student.class_id.class_group_id,
                subject_conf_id=subject
            ).select_related('mark_type_id')

            max_marks = sum((mc.mark or 0) for mc in mark_configs)
            total_marks_possible += max_marks

            marks = Subject_mark.objects.filter(
                student_id=student.id,
                examname_id=selected_exam_id,
                mark_id__subject_conf_id=subject
            ).select_related("mark_id__mark_type_id")

            total_marks = 0
            for mark in marks:
                if not mark.mark_id:
                    continue
                mark_type_name = mark.mark_id.mark_type_id.name.upper()
                if mark_type_name not in mark_type_list:
                    mark_type_list.append(mark_type_name)
                obtained = round(mark.mark or 0, 2)
                student_data["subjects"][subject_name]["marks"][mark_type_name] = obtained
                total_marks += obtained

            percentage = (total_marks / max_marks) * 100 if max_marks > 0 else 0
            gpa, grade = get_grade(percentage)

            student_data["subjects"][subject_name]["total"] = round(total_marks, 2)
            student_data["subjects"][subject_name]["gpa"] = gpa
            student_data["subjects"][subject_name]["grade"] = grade

            if str(grade).upper() == "F":
                any_fail = True

            total_marks_obtained += total_marks
            total_gpa_sum += gpa
            total_gpa_count += 1 if max_marks > 0 else 0

        student_data["total_marks"] = round(total_marks_obtained, 2)
        student_data["total_gpa"] = (
            round(total_gpa_sum / total_gpa_count, 2) if total_gpa_count > 0 else 0
        )
        final_percentage = (
            (total_marks_obtained / total_marks_possible) * 100
            if total_marks_possible > 0 else 0
        )
        student_data["final_grade"] = get_grade(final_percentage)[1]

        if any_fail:
            student_data["status"] = "Fail"
            student_data["total_gpa"] = 0.00
            student_data["final_grade"] = "F"

        tabulation_data.append(student_data)

    return tabulation_data, subject_list, mark_type_list


def tabulation_sheet_two(request):
    classes = ClassConfig.objects.all()
    exams = Examname.objects.all()

    selected_class_id = request.POST.get("class_id")
    selected_exam_id = request.POST.get("exam_id")

    tabulation_data, subject_list, mark_type_list = _build_tabulation(
        selected_class_id, selected_exam_id
    )

    context = {
        "classes": classes,
        "exams": exams,
        "tabulation_data": tabulation_data,
        "subject_list": subject_list,
        "mark_type_list": mark_type_list,
        "selected_class_id": selected_class_id,
        "selected_exam_id": selected_exam_id,
        "heading": "Result",
        "subheading": "Tabulation Sheet",
    }
    return render(request, "exams/mark/tabulation_sheet_two.html", context)


def tabulation_pdf(request):
    """Landscape PDF — preview er SHOMAN data. Institute name dynamic."""
    selected_class_id = request.GET.get("class_id")
    selected_exam_id = request.GET.get("exam_id")

    tabulation_data, subject_list, mark_type_list = _build_tabulation(
        selected_class_id, selected_exam_id
    )

    # ---- Header meta (dynamic institute + class/exam info) ----
    institute = Institute.objects.first()
    class_config = ClassConfig.objects.filter(id=selected_class_id).select_related(
        'class_group_id', 'class_group_id__class_id', 'class_group_id__group_id',
        'section_id', 'shift_id'
    ).first()
    exam_obj = Examname.objects.filter(id=selected_exam_id).first()

    class_meta = {}
    if class_config:
        cg = class_config.class_group_id
        class_meta = {
            "class_name": cg.class_id.name if cg and cg.class_id else "",
            "group": cg.group_id.name if cg and cg.group_id else "",
            "section": class_config.section_id.name if class_config.section_id else "",
            "shift": class_config.shift_id.name if class_config.shift_id else "",
        }

    # ---- Dynamic sizing (subject beshi hole choto font) ----
    subject_count = len(subject_list) or 1
    base_font_size = max(6, 11 - (subject_count // 3))
    base_padding = max(2, 5 - (subject_count // 4))

    context = {
        "tabulation_data": tabulation_data,
        "subject_list": subject_list,
        "mark_type_list": mark_type_list,
        "font_size": base_font_size,
        "padding": base_padding,
        "institute": institute,
        "class_meta": class_meta,
        "exam_name": exam_obj.name if exam_obj else "",
    }

    html_string = render_to_string("exams/mark/tabulation_pdf_template.html", context)
    pdf_file = HTML(
        string=html_string, base_url=request.build_absolute_uri('/')
    ).write_pdf(
        stylesheets=[CSS(string=f"""
            @page {{ size: legal landscape; margin: 8mm; }}
            table {{ table-layout: fixed; width: 100%; }}
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