from django.urls import path
from .views import *
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .api_views import *

urlpatterns = [
    # path('fpanel',school,name='fpanel' ), 
    path('contact/',fcontact,name='fcontact' ), 
    path('fnot/',fnot,name='fnot'),
    path('fstudent_list/',fstudent_list,name='fstudent_list'),
    path('fteacher_list/',fteacher_list,name='fteacher_list'),
    path('fstaff_list/',fstaff_list,name='fstaff_list'),
    path('institute_details/',institute_details,name='institute_details'),
    path('fclass_routine/',fclass_routine,name='fclass_routine'),
    path('fteacher_routine/',fteacher_routine,name='fteacher_routine'),
    path('f_student_attendance/',f_student_attendance,name='f_student_attendance'),
    path('video_gallery/',video_gallery,name='video_gallery'),
    path('photo_gallery/',photo_gallery,name='photo_gallery'),
    path('f_syllabus/',f_syllabus,name='f_syllabus'),
    path('assignment/',list_assignment,name='assignment'),
    path('hand_book/',list_hand_book,name='hand_book'),
    path('home_work/',list_home_work,name='home_work'),
    path('class_notes/',list_class_notes,name='class_notes'),
    path('others_download/',list_others_download,name='others_download'), 

    path('site_settings/banner/',banner,name='banner' ),
    path('list_banner/',list_banner,name='list_banner' ),
    path('add_banner/',add_banner,name='add_banner' ),
    path('banner/<int:pk>/edit',edit_banner,name='edit_banner'),
    path('banner/<int:pk>/del',del_banner,name='del_banner'), 

    path('site_settings/service/',service,name='service' ),
    path('list_service/',list_service,name='list_service' ),
    path('add_service/',add_service,name='add_service' ),
    path('service/<int:pk>/edit',edit_service,name='edit_service'),
    path('service/<int:pk>/del',del_service,name='del_service'), 
 
    path('site_settings/page_content/',page_content,name='page_content' ),
    path('page_content_list/',page_content_list,name='page_content_list' ),
    path('page_content/<int:pk>/edit',edit_page_content,name='edit_page_content'),

    path('site_settings/gallery/',gallery,name='gallery' ),
    path('list_gallery/',list_gallery,name='list_gallery' ),
    path('add_gallery/',add_gallery,name='add_gallery' ),
    path('gallery/<int:pk>/edit',edit_gallery,name='edit_gallery'),
    path('gallery/<int:pk>/del',del_gallery,name='del_gallery'), 

    path('site_settings/vgallery/',vgallery,name='vgallery' ),
    path('list_vgallery/',list_vgallery,name='list_vgallery' ),
    path('add_vgallery/',add_vgallery,name='add_vgallery' ),
    path('vgallery/<int:pk>/edit',edit_vgallery,name='edit_vgallery'),
    path('vgallery/<int:pk>/del',del_vgallery,name='del_vgallery'), 

    path('site_settings/testimonial/',testimonial,name='testimonial' ),
    path('list_testimonial/',list_testimonial,name='list_testimonial' ),
    path('add_testimonial/',add_testimonial,name='add_testimonial' ),
    path('testimonial/<int:pk>/edit',edit_testimonial,name='edit_testimonial'),
    path('testimonial/<int:pk>/del',del_testimonial,name='del_testimonial'), 

    path('site_settings/contact/',contact,name='contact' ),
    path('list_contact/',list_contact,name='list_contact' ),
    path('add_contact/',add_contact,name='add_contact' ),
    path('contact/<int:pk>/edit',edit_contact,name='edit_contact'),
    path('contact/<int:pk>/del',del_contact,name='del_contact'),

    path('password-reset/', PasswordResetView.as_view(template_name='website/auth/password_reset.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='website/auth/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='website/auth/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='website/auth/password_reset_complete.html'),name='password_reset_complete'),

    path('banners/', BannerListAPIView.as_view(), name='banner-list'),
    path('school-history/', SchoolHistoryListAPIView.as_view(), name='school-history-list'),
    path('messages-from-head/', MsgFromHeadListAPIView.as_view(), name='msg-from-head-list'),
    path('messages-from-other/', MsgFromOtherListAPIView.as_view(), name='msg-from-other-list'),
    path('important-links/', ImportantLinkListAPIView.as_view(), name='important-link-list'),
    path('credentials/', CredentialsListAPIView.as_view(), name='credentials-list'),
    path('features/', FeatureListAPIView.as_view(), name='feature-list'),
    path('iconic-students/', IconicStudentListAPIView.as_view(), name='iconic-student-list'),
    path('gallery/', GalleryListAPIView.as_view(), name='gallery-list'),
    path('video-gallery/', VideoGalleryListAPIView.as_view(), name='video-gallery-list'),
    path('testimonials/', TestimonialListAPIView.as_view(), name='testimonial-list'),
    path('contacts/', ContactListAPIView.as_view(), name='contact-list'),
    path('link-names/', LinkNameListAPIView.as_view(), name='link-name-list'),
    path('links/', LinkListAPIView.as_view(), name='link-list'),
    path('committees/', CommitteeListAPIView.as_view(), name='committee-list'),
    path('welcome-speeches/', WelcomeSpeechListAPIView.as_view(), name='welcome-speech-list'),
    path('notices/', NoticeListAPIView.as_view(), name='notice-list'),
    path('downloads/', DownloadListAPIView.as_view(), name='download-list'),
    path('site-color/', SiteColorAPIView.as_view(), name='site-color'),
    path('seat-info/', SeatInfoListView.as_view(), name='seat-info-list'),
    path('dress-code/', DressCodeListView.as_view(), name='dress-code-list'),
    path('public-msg/', PublicMsgCreateAPIView.as_view(), name='public_msg_create'),

    
]