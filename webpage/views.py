from django.shortcuts import render, get_object_or_404
from .models import *
from exam.models import Examname,Syllabus
from crucial.models import Notice,Download
from .forms import *
from user.decorators import *
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.http import HttpResponse
import json
from core.models import ClassConfig,Admission_Year,StudentClass
from user.models import StudentProfile
from attendance.models import Holiday,StudentAttendance
from miscellaneous.models import Institute
from datetime import datetime
from itertools import groupby
from operator import itemgetter
from django.db.models import Q 
from django.utils import timezone
from crucial.models import Download

def fcontact(request):
    contact = Contact.objects.filter(status='ACTIVE').last()
    context={
        'contact':contact,
    }
    return render(request, 'fsite/contact.html',context)

def fnot(request):
    return render(request, 'fsite/404.html')

def fstudent_list(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    classList= ClassConfig.objects.filter(session_year=admission_year)
    classconf =None
    studentList=None
    if request.method=='POST':
        class_id= request.POST.get('class_name_id')
        studentList = StudentProfile.objects.filter(class_id=class_id).order_by("roll_no")
            
    context={
        'classList':classList,
        # 'classconf':classconf,
        'studentList':studentList
    }
    return render(request, 'fsite/student_list.html',context)

def fteacher_list(request):
    teacherList= Teacher.objects.all()
    context={'teacherList':teacherList}
    return render(request, 'fsite/teacher_list.html',context)

def fstaff_list(request):
    staffList= Staff.objects.all()
    context={'staffList':staffList}
    return render(request, 'fsite/staff_list.html',context)

def institute_details(request):
    institute=Institute.objects.latest('id')
    context={'institute':institute}
    return render(request, 'fsite/institute_details.html',context)

def fclass_routine(request):
   classList=ClassConfig.objects.all()
   context={
       'classList':classList
   }
   return render(request, 'fsite/class_routine.html',context) 

def fteacher_routine(request):
   teacherList=Teacher.objects.all()
   context={
       'teacherList':teacherList
   }
   return render(request, 'fsite/teacher_routine.html',context) 

def f_student_attendance(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    classList = ClassConfig.objects.filter(session_year=admission_year)
    condensed_data = [] 
    holidays = []
    class_name = None

    if request.user.is_authenticated and is_staff_or_in_group(request.user, "student","parent"):
        requested_user = request.user


    if request.method == 'POST':
        month = request.POST.get('searchMonth')
        class_id = request.POST.get('class_name_id')
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
                name__class_id=class_id
            )

        attendancelist = list(attendance_records.values('name__student_field__name', 'status', 'attendance_date'))

        # Group attendance records by student name
        grouped_attendance = {name: list(group) for name, group in groupby(attendancelist, key=itemgetter('name__student_field__name'))}

        for name, records in grouped_attendance.items():
            attendance_dates = [record['attendance_date'].day for record in records if record['status']]
            condensed_data.append({'name': name, 'attendance': attendance_dates})


        holiday_records = Holiday.objects.filter(
            holiday_date__year=search_date.year,
            holiday_date__month=search_date.month
        )
        holidaylist = list(holiday_records.values('holiday_date'))

        holidays = [date['holiday_date'].day for date in holidaylist]

        

    context = {
        'classList': classList,
        'heading': 'Attendance Report',
        'subheading': 'Student Attendance',
        'attendanceData': condensed_data,
        'holidayData': holidays,
        'class_name':class_name
    }
    return render(request, 'fsite/student_attendance.html', context)

def video_gallery(request):
    vedioList=Video_Gallery.objects.filter(status='ACTIVE')
    context = {
        'vedioList':vedioList
    }
    return render(request, 'fsite/video_gallery.html',context)

def photo_gallery(request):
    photoList=Gallery.objects.filter(status='ACTIVE')
    context = {
        'galleryList':photoList
    }
    return render(request, 'fsite/picture_gallery.html',context)

#--------------------- Banner --------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def banner(request):
    context = {
        'heading': 'Website Settings',
        'subheading': 'Banner',
    }
    return render(request, 'website/banner/banner.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_banner(request):
    bannerlist = Banner.objects.all()
    context = {
        'bannerlist': bannerlist
    }
    return render(request, 'website/banner/list_banner.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({ 
                    "messages": 'Success',
                    "bannerChanged": "bannerChanged"
                })})
    else:
        form = BannerForm()

    context = {
        'form': form,
    }

    return render(request, 'website/banner/add_banner.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_banner(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST,request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "bannerChanged": "bannerChanged"
                })})
    else:
        form = BannerForm(instance=banner)

    context = {
        'form': form
    }

    return render(request, 'website/banner/add_banner.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_banner(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'bannerChanged'})


#--------------------- Service --------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def service(request):
    context = {
        'heading': 'Website Settings',
        'subheading': 'Service',
    }
    return render(request, 'website/service/service.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_service(request):
    servicelist = Service.objects.all()
    context = {
        'servicelist': servicelist
    }
    return render(request, 'website/service/list_service.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({ 
                    "messages": 'Success',
                    "serviceChanged": "serviceChanged"
                })})
    else:
        form = ServiceForm()

    context = {
        'form': form,
    }

    return render(request, 'website/service/add_service.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST,request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "serviceChanged": "serviceChanged"
                })})
    else:
        form = ServiceForm(instance=service)

    context = {
        'form': form
    }

    return render(request, 'website/service/add_service.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'serviceChanged'})



#--------------------- Gallery --------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def gallery(request):
    context = {
        'heading': 'Website Settings',
        'subheading': 'Gallery',
    }
    return render(request, 'website/gallery/gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_gallery(request):
    gallerylist = Gallery.objects.all()
    context = {
        'gallerylist': gallerylist
    }
    return render(request, 'website/gallery/list_gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_gallery(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Galary has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({ 
                    "messages": 'Success',
                    "galaryChanged": "galaryChanged"
                })})
    else:
        form = GalleryForm()

    context = {
        'form': form,
    }

    return render(request, 'website/gallery/add_gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_gallery(request, pk):
    galary = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        form = GalleryForm(request.POST,request.FILES, instance=galary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Galary has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "galaryChanged": "galaryChanged"
                })})
    else:
        form = GalleryForm(instance=galary)

    context = {
        'form': form
    }

    return render(request, 'website/gallery/add_gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_gallery(request, pk):
    galary = get_object_or_404(Gallery, pk=pk)
    galary.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'galaryChanged'})


#---------------------Video Gallery --------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def vgallery(request):
    context = {
        'heading': 'Website Settings',
        'subheading': 'Video Gallery',
    }
    return render(request, 'website/vgallery/gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_vgallery(request):
    gallerylist = Video_Gallery.objects.all()
    context = {
        'gallerylist': gallerylist
    }
    return render(request, 'website/vgallery/list_gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_vgallery(request):
    if request.method == 'POST':
        form = VGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Galary has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({ 
                    "messages": 'Success',
                    "galleryChanged": "galleryChanged"
                })})
    else:
        form = VGalleryForm()

    context = {
        'form': form,
    }

    return render(request, 'website/vgallery/add_gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_vgallery(request, pk):
    galary = get_object_or_404(Video_Gallery, pk=pk)
    if request.method == 'POST':
        form = VGalleryForm(request.POST,request.FILES, instance=galary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Galary has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "galleryChanged": "galleryChanged"
                })})
    else:
        form = VGalleryForm(instance=galary)

    context = {
        'form': form
    }

    return render(request, 'website/vgallery/add_gallery.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_vgallery(request, pk):
    gallery = get_object_or_404(Video_Gallery, pk=pk)
    gallery.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'galleryChanged'})



#--------------------- Massage From Head --------------------
@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def page_content(request):
    context = {
        'heading': 'Website Settings',
        'subheading': 'Message',
    }
    return render(request, 'website/page/page_content.html', context)


@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def page_content_list(request):
    page_content_list=Page_content.objects.all()
    print(page_content_list)
    context = {
        'page_content_list': page_content_list,
    }
    return render(request, 'website/page/list_page_content.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_page_content(request, pk):
    print(f"Received request with pk: {pk}")  # Debug print

    # Retrieve the page object or return a 404 if not found
    page = get_object_or_404(Page_content, pk=pk)

    if request.method == 'POST':
        print("Processing POST request")  # Debug print
        
        # Initialize the form with POST data and files
        form = PageFrom(request.POST, request.FILES, instance=page)
        
        if form.is_valid():
            print("Form is valid")  # Debug print
            form.save()
            messages.success(request, 'Data has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                "messages": 'Success',
                "contentChanged": "contentChanged"
            })})
        else:
            # Print form errors to the console
            print(f"Form errors: {form.errors}")  # Debug print
        
    else:
        print("Processing GET request")  # Debug print
        # Initialize the form with existing page data
        form = PageFrom(instance=page)

    # Prepare the context with the form
    context = {
        'form': form
    }

    # Render the template with the form in the context
    return render(request, 'website/page/add_page_content.html', context)


#--------------------- Testimonial --------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def testimonial(request):
    context = {
        'heading': 'Website Settings',
        'subheading': 'Testimonial',
    }
    return render(request, 'website/testimonial/testimonial.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_testimonial(request):
    testimoniallist = Testimonial.objects.all()
    context = {
        'testimoniallist': testimoniallist
    }
    return render(request, 'website/testimonial/list_testimonial.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({ 
                    "messages": 'Success',
                    "testimonialChanged": "testimonialChanged"
                })})
    else:
        form = TestimonialForm()

    context = {
        'form': form,
    }

    return render(request, 'website/testimonial/add_testimonial.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST,request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "testimonialChanged": "testimonialChanged"
                })})
    else:
        form = TestimonialForm(instance=testimonial)

    context = {
        'form': form
    }

    return render(request, 'website/testimonial/add_testimonial.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'testimonialChanged'})



#--------------------- Contact --------------------

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def contact(request):
    context = {
        'heading': 'Website Settings',
        'subheading': 'Contact',
    }
    return render(request, 'website/contact/contact.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def list_contact(request):
    contactlist = Contact.objects.all()
    context = {
        'contactlist': contactlist
    }
    return render(request, 'website/contact/list_contact.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def add_contact(request):
    if request.method == 'POST':
        form = ContactFrom(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact has been Saved ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({ 
                    "messages": 'Success',
                    "contactChanged": "contactChanged"
                })})
    else:
        form = ContactFrom()

    context = {
        'form': form,
    }

    return render(request, 'website/contact/add_contact.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def edit_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = ContactFrom(request.POST,request.FILES, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact has been Updated ! ! !')
            return HttpResponse(status=200, headers={'HX-Trigger': json.dumps({
                    "messages": 'Success',
                    "contactChanged": "contactChanged"
                })})
    else:
        form = ContactFrom(instance=contact)

    context = {
        'form': form
    }

    return render(request, 'website/contact/add_contact.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: is_staff_or_has_role(user, roles=['Manager','HR']))
def del_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'contactChanged'})


#--------------------- Assignment --------------------
def f_syllabus(request):
    admission_year = Admission_Year.objects.latest('updated_at')
    class_instance,syllabusList=None,None
    classList= StudentClass.objects.filter(session_year=admission_year)
    examList=Examname.objects.filter(session_year=admission_year)
    

    if request.method=='POST':
            class_id= request.POST.get("class_name_id")
            class_instance= get_object_or_404(StudentClass,pk=class_id)
            exam_id= request.POST.get("exam_name_id")
            exam_instance= get_object_or_404(Examname,pk=exam_id)
            syllabusList = Syllabus.objects.filter(Q(exam_name=exam_instance) & Q(classname=class_instance))
            print(syllabusList)

    context = {
        'syllabusList':syllabusList,
        'classList':classList,
        'examList':examList,
        'class_instance':class_instance
    }
    return render(request, 'fsite/download/syllabus.html', context)

def list_assignment(request):
    try:
        admission_year = Admission_Year.objects.latest('updated_at')
        classList= ClassConfig.objects.filter(session_year=admission_year)
        assignment_list,class_instance=None,None

        if request.method=='POST':
            class_id= request.POST.get("class_name_id")
            class_instance= get_object_or_404(ClassConfig,pk=class_id)
            assignment_list = Download.objects.filter(Q(download_type='Assignment') & Q(class_id=class_instance)).order_by('-created_at')

    except Page_content.DoesNotExist:
        classList = None     
    context = {
        'classList':classList,
        'class_instance':class_instance,
        'assignment_list': assignment_list
    }
    return render(request, 'fsite/download/assignment.html', context)

def list_hand_book(request):
    try:
        admission_year = Admission_Year.objects.latest('updated_at')
        classList= ClassConfig.objects.filter(session_year=admission_year)
        hand_book_list,class_instance=None,None

        if request.method=='POST':
            class_id= request.POST.get("class_name_id")
            class_instance= get_object_or_404(ClassConfig,pk=class_id)
            hand_book_list = Download.objects.filter(Q(download_type='Hand Book') & Q(class_id=class_instance)).order_by('-created_at')

    except Page_content.DoesNotExist:
        classList = None
            
    context = {
        'classList':classList,
        'class_instance':class_instance,
        'hand_book_list': hand_book_list
    }
    return render(request, 'fsite/download/hand_book.html', context)

def list_home_work(request):
    try:
        admission_year = Admission_Year.objects.latest('updated_at')
        classList= ClassConfig.objects.filter(session_year=admission_year)
        home_work_list,class_instance=None,None

        if request.method=='POST':
            class_id= request.POST.get("class_name_id")
            class_instance= get_object_or_404(ClassConfig,pk=class_id)
            home_work_list = Download.objects.filter(Q(download_type='Home Work') & Q(class_id=class_instance)).order_by('-created_at')

    except Page_content.DoesNotExist:
        classList = None
            
    context = {
        'classList':classList,
        'class_instance':class_instance,
        'home_work_list': home_work_list
    }
    return render(request, 'fsite/download/home_work.html', context)

def list_class_notes(request):
    try:
        admission_year = Admission_Year.objects.latest('updated_at')
        classList= ClassConfig.objects.filter(session_year=admission_year)
        class_notes_list,class_instance=None,None

        if request.method=='POST':
            class_id= request.POST.get("class_name_id")
            class_instance= get_object_or_404(ClassConfig,pk=class_id)
            class_notes_list = Download.objects.filter(Q(download_type='Class Notes') & Q(class_id=class_instance)).order_by('-created_at')

    except Page_content.DoesNotExist:
        classList = None
            
    context = {
        'classList':classList,
        'class_instance':class_instance,
        'class_notes_list': class_notes_list
    }
    return render(request, 'fsite/download/class_notes.html', context)


def list_others_download(request):
    try:
        admission_year = Admission_Year.objects.latest('updated_at')
        classList= ClassConfig.objects.filter(session_year=admission_year)
        others_download_list,class_instance=None,None

        if request.method=='POST':
            class_id= request.POST.get("class_name_id")
            class_instance= get_object_or_404(ClassConfig,pk=class_id)
            others_download_list = Download.objects.filter(Q(download_type='Others Download') & Q(class_id=class_instance)).order_by('-created_at')

    except Page_content.DoesNotExist:
        classList = None
            
    context = {
        'classList':classList,
        'class_instance':class_instance,
        'others_download_list': others_download_list
    }
    return render(request, 'fsite/download/others_download.html', context)

