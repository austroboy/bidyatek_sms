from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import *
from .forms import *
from user.decorators import *
from django.contrib.auth.decorators import user_passes_test, login_required
from core.models import StudentClass
from user.forms import *
from django.db.models import Q
from datetime import datetime
from django.forms import modelformset_factory


# Institute Profile
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"student", "parent","teacher","staff", roles=['Manager','HR']))
def institute(request):
    try:
        institute = Institute.objects.latest('id')  # Fetch the latest institute
    except Institute.DoesNotExist:
        institute = None  # No institute exists

    if request.method == 'POST':
        form = InstituteForm(request.POST, request.FILES, instance=institute)
        if form.is_valid():
            form.save()
            if institute:  # If updating
                messages.success(request, 'Institute Information has been updated!')
            else:  # If creating
                messages.success(request, 'Institute Information has been added!')
            return redirect('institute')
    else:
        form = InstituteForm(instance=institute)

    context = {
        'heading': 'Institute Information',
        'subheading': 'Information',
        'institute': institute,
        'form': form,  # Pass the form to render the Add/Edit form
    }
    return render(request, 'miscellaneous/institute.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def institute_edit(request,id):

    institute= Institute.objects.get(id=id)
    if request.method == 'POST':
        form = InstituteForm(request.POST, request.FILES, instance=institute)
        if form.is_valid():
            form.save()
            messages.success(request, 'Institute Information has been Updated ! ! !')
        
            return redirect('institute') 
    else:
        form = InstituteForm(instance=institute)

    context={
            'form':form,
        }
    return render(request ,'miscellaneous/add_institute.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"student", "parent","teacher","staff", roles=['Manager','HR', 'Accountant']))
def event(request):

    context={
        'heading':'Academic Events',
        'subheading':'Events'
    }

    return render(request, 'miscellaneous/events.html',context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"student", "parent","teacher","staff", roles=['Manager','HR', 'Accountant']))
def eventview(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    events = Event.objects.filter(academic_year=admission_year)
    eventlist = [] 

    for event in events:
        eventlist.append({
            'title': event.title,
            'id': event.id,
            'start': event.start.strftime("%Y-%m-%d %H:%M:%S") if event.start else None,  # Handle None case
            'end': event.end.strftime("%Y-%m-%d %H:%M:%S") if event.end else None,      # Handle None case
        })

    return JsonResponse(eventlist, safe=False)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_event(request):
    current_user = request.user
    
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)

    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Event(title=str(title), start=start, end=end,academic_year=admission_year,created_by=current_user)
    event.save()
    data = {} 
    return JsonResponse(data)
 
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def update_event(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Event.objects.get(id=id)
    event.start = start
    event.end = end
    event.title = title
    event.academic_year = admission_year
    event.save()
    data = {}
    return JsonResponse(data)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def remove_event(request):
    id = request.GET.get("id", None)
    event = Event.objects.get(id=id)
    event.delete()
    data = {}
    return JsonResponse(data)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user,"student", "parent","teacher","staff", roles=['Manager','HR']))
def eventdetail(request):
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    events=Event.objects.filter(academic_year=admission_year).order_by('start')
    context={
        'heading':'Academic Events',
        'subheading':'Event List',
        'eventlist':events
    }
    return render(request, 'miscellaneous/event_list.html',context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_event(request,id):
    
    event_instance = get_object_or_404(Event, id=id )
    if request.method == 'POST':
        form = EventFrom(request.POST,instance=event_instance )
        if form.is_valid():
            current_user = request.user
            event_from = form.save(commit=False)
            event_from.updated_by = current_user
            event_from.save()
            messages.success(request, 'Seleted Event has been Updated ! ! !')
            return redirect('event_detail')

    else:
        form = EventFrom(instance=event_instance)

    context = {
        'form': form,
        'heading': 'Academic Events',
        'subheading': 'Edit Event',
    }
    return render(request, 'miscellaneous/event_edit.html',context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_event(request,id):
    event = Event.objects.get(id=id)
    event.delete()
    messages.success(request, 'Seleted Event has been deleted ! ! !')
    return redirect('event_detail')


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager', 'HR']))
def generate_testimonial_report(request): 
    if request.method == 'GET':
        student_id = request.GET.get('student_id')
        try:
            student_instance = get_object_or_404(StudentProfile, id=student_id)
            testimonial_instance = get_object_or_404(Testimonial, student_id=student_instance)
            parent_instance = student_instance.parent_id.parent_profile
            institute = Institute.objects.latest('id')
            data = {
                'student_name': student_instance.student_field.name or '',
                'father_name': parent_instance.father_name or '',
                'mother_name': parent_instance.mother_name or '',
                'village_name': student_instance.village or '',
                'post_office': student_instance.post_office or '',
                'police_station_upazilla': student_instance.ps_or_upazilla or '',
                'district': student_instance.district or '',
                'exam_name': testimonial_instance.exam or '',
                'exam_center': testimonial_instance.exam_center or '',
                'exam_held_date': testimonial_instance.exam_held_date or '',
                'board_name': institute.education_board_id.board_name or '',
                'group_name': testimonial_instance.group_name or '',
                'roll_no': testimonial_instance.e_roll or '',
                'registration_no': testimonial_instance.r_no or '',
                'session': testimonial_instance.session or '',
                'result': testimonial_instance.result or '',
                'date_of_birth': student_instance.student_field.dob or '',
                'issue_date': testimonial_instance.issue_date or '',
                'serial': testimonial_instance.serial or '',
            }
            return JsonResponse(data, status=200)
        except StudentProfile.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_testmonial(request):
    institute=Institute.objects.latest('id')
    current_year = str(datetime.now().year)
    admission_year = Admission_Year.objects.get(name=current_year)
    classList = StudentClass.objects.all()
    try:
        testmonial_settings = TestmonialSettings.objects.latest('id')
    except TestmonialSettings.DoesNotExist:
        testmonial_settings = None

    studentlist = None
    if request.method == 'POST' and 'class_id' in request.POST:
        class_id = request.POST.get("class_id")
        class_instance = get_object_or_404(StudentClass, pk=class_id)
        studentlist = StudentProfile.objects.filter(
            Q(class_id__class_group_id__class_id=class_instance) &
            Q(admission_year_id=admission_year) & 
            Q(student_field__status="Active")
        )
    
    if request.method == 'POST' and 'settings_form' in request.POST:
        settings = TestmonialSettings.objects.first() or TestmonialSettings()
        form = TestmonialSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved successfully!')
            return redirect('list_testmonial')
        
        
    else:
        settings = TestmonialSettings.objects.first() or TestmonialSettings()
        form = TestmonialSettingsForm(instance=settings)

    context = {
        'classList': classList,
        'studentlist': studentlist,
        'testmonial_settings': testmonial_settings,
        'institute':institute,
        'heading': 'Student',
        'subheading': 'Testmonial',
        'form': form
    }

    return render(request, 'report/student_testimonial.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def testimonial_info_add(request,pk):
    student_instance= StudentProfile.objects.get(id=pk)
    student_id=student_instance.student_field
    institute=Institute.objects.latest('id')
    testimonial_instance, created = Testimonial.objects.get_or_create(student_id=student_instance)
    parent_instance = student_instance.parent_id.parent_profile
    if request.method == "POST":
        father_name = request.POST.get('father_name')
        mother_name = request.POST.get('mother_name')
        village = request.POST.get('village')
        post_office = request.POST.get('post_office')
        police_station = request.POST.get('police_station')
        district = request.POST.get('district')
        exam_name = request.POST.get('exam_name')
        exam_center = request.POST.get('exam_center')
        exam_date = request.POST.get('exam_held_date')
        board_name = request.POST.get('board_name')
        group_name = request.POST.get('group_name')
        roll_no = request.POST.get('roll_no')
        registration_no = request.POST.get('registration_no')
        session = request.POST.get('session')
        result = request.POST.get('result')
        dob = request.POST.get('dob')
        issue_date = request.POST.get('issue_date')

        testimonial_instance.exam = exam_name
        testimonial_instance.exam_center = exam_center
        testimonial_instance.e_roll = roll_no
        testimonial_instance.r_no = registration_no
        testimonial_instance.exam_held_date = exam_date
        testimonial_instance.group_name = group_name
        testimonial_instance.session = session
        testimonial_instance.result = result
        testimonial_instance.issue_date = issue_date if issue_date else None
        testimonial_instance.save()
        
        student_instance.village = village
        student_instance.post_office = post_office
        student_instance.ps_or_upazilla = police_station
        student_instance.district = district
        student_instance.save()

        parent_instance.father_name =father_name
        parent_instance.mother_name =mother_name
        parent_instance.save()

        student_id.dob=dob
        student_id.save()
        messages.success(request, 'Data Update Completed!')
        return redirect('testimonial_info_add', pk=pk)
    context = {
        'student_instance':student_instance,
        'institute':institute,
        'testimonial_instance':testimonial_instance,
        'heading': 'Student',
        'subheading': 'Testmonial Data',
    }
    return render(request, 'core/user/student_testimonial_data.html', context)

def list_weekend_config(request):
    # Fetch existing data
    weekend_days = WeekendDay.objects.all()
    timings = Timing.objects.all()

    # Define formsets
    WeekendDayFormSet = modelformset_factory(WeekendDay, form=WeekendDayForm, extra=1, can_delete=True)
    TimingFormSet = modelformset_factory(Timing, form=TimingForm, extra=1, can_delete=True)

    weekend_formset = WeekendDayFormSet(queryset=weekend_days)
    timing_formset = TimingFormSet(queryset=timings)

    if request.method == 'POST':
        # Determine which form was submitted
        if 'weekend_submit' in request.POST:
            weekend_formset = WeekendDayFormSet(request.POST, queryset=weekend_days)
            if weekend_formset.is_valid():
                weekend_formset.save()
                messages.success(request, "Weekend Days configuration saved successfully!")  # Add success message

                return redirect('list_weekend_config')  # Redirect after saving

        if 'timing_submit' in request.POST:
            timing_formset = TimingFormSet(request.POST, queryset=timings)
            if timing_formset.is_valid():
                timing_formset.save()
                messages.success(request, "Working Hours configuration saved successfully!")  # Add success message

                return redirect('list_weekend_config')

    context = {
        'weekend_formset': weekend_formset,
        'timing_formset': timing_formset,
        'heading': 'Settings',
        'subheading': 'Academic Timing',
    }
    return render(request, 'miscellaneous/manage_weekend_timing.html', context)
