from django.urls import path, include
from .api_views import *
from .views import *

urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('search-students/', search_students, name='search_students'),

    path('student/add_student/',add_student,name='add_student'),
    path('student/list_student/',list_student,name='list_student'),
    path('edit_student/<int:id>/',edit_student,name='edit_student'),
    path('bulk-update-student-id/',bulk_update_student_id, name='bulk_update_student_id'),
    path('change_status_student/<int:id>/',change_status_student,name='change_status_student'),
    path('student_import_data/', student_import_data, name='student_import_data'),
    
    path('students/export/excel/', export_students_excel, name='export_excel'),
    path('students/export/pdf/', export_students_pdf, name='export_pdf'),
    
    path('student/student_id_data/', student_id_data, name='student_id_data'),  
    path('student/rfid_update/', rfid_update, name='rfid_update'),  
    path('update-rfid/', update_rfid, name='update_rfid'),

    path('get_student_classes/',get_student_classes, name='get_student_classes'),
    path('student/list_migrations/', list_migrations, name='list_migrations'),
    path('student_data/', student_data, name='student_data'),  
    
    
    path('staff/add_staff/',add_staff,name='add_staff'),
    path('staff/list_staff/',list_staff,name='list_staff'),
    path('edit_staff/<int:id>',edit_staff,name='edit_staff'),
    path('change_status_staff/<int:id>',change_status_staff,name='change_status_staff'),
    path('staff_import_data/', staff_import_data, name='staff_import_data'),
    path('staff/staff_id_data/', staff_id_data, name='staff_id_data'),
    
    path('parent/add_parent/',add_parent,name='add_parent'),
    path('parent/list_parent/',list_parent,name='list_parent'),
    path('edit_parent/<int:id>',edit_parent,name='edit_parent'),
    path('change_status_parent/<int:id>',change_status_parent,name='change_status_parent'),

    path('edit_profile/',edit_profile,name='edit_profile'),

    # path('permission/',Permission_User.as_view(),kwargs={'id': None}, name='permission'),
    # path('permission/<id>/',Permission_User.as_view(), name='permission'),
    # path('permissions/',Permission_User.as_view(),kwargs={'id': None}, name='permissions'),
    # path('permissions/<id>/',Permission_User.as_view(), name='permission'),
    # path('permission/', PermissionUserView.as_view(), kwargs={'id': None}, name='permission'),
    # path('user_permissions/<int:group_id>/', PermissionUserView.as_view(), name='user_permissions'),
    path('student/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('api/student-profiles/', StudentProfileListView.as_view(), name='student_profiles'),
    path('api/student-profile/<int:pk>/', StudentProfileRetrieveAPIView.as_view(), name='student-detail'),
    path('api/staff-profiles/', StaffProfileListView.as_view(), name='staff_profiles'),
    path('api/create-student-parent/', CreateStudentParentAPIView.as_view(), name='create-student-parent'),
    
    path('bulk-upload-emails/', bulk_upload_emails, name='bulk_upload_emails'),
    path('process-email-upload/', process_email_upload, name='process_email_upload'),
    
    path('admission/', AdmissionFormView.as_view(), name='admission_form'),
    path('admission/admit-card/<str:applicant_id>/', AdmitCardView.as_view(), name='admit_card'),
    path('admission/applicants/', admission_applicants_list, name='admission_applicants_list'),
    path('admission/migrate/<str:applicant_id>/', migrate_applicant, name='migrate_applicant'),
    path('admission/payment-callback/', payment_callback, name='admission_payment_callback'),
    path('admission/payment/<str:applicant_id>/', initiate_admission_payment, name='initiate_admission_payment'),
    path('admission/payment/callback/', payment_callback, name='payment_callback'),
    path('admission/payment/fail/', payment_fail, name='payment_fail'),
    path('admission/payment/cancel/', payment_cancel, name='payment_cancel'),
    
    #class xi
    path('admissions/', admission_form, name='admission_form'),
    path('download-pdf/<int:admission_id>/', download_pdf, name='download_pdf'),
    
    path('register/', registration_view, name='registration'),
    path('registration-success/<int:registration_id>/', registration_success, name='registration_success'),
    path('users/', registered_users_view, name='registered_users'),
    
    # student information download
    path('download-student-data/', download_student_data, name='download_student_data'),
    path('download-subjects/', download_student_subjects, name='download_student_subjects'),
    
    path('manage-student-status/', manage_student_status, name='manage_student_status'),
    path('bulk-update-student-status/', bulk_update_student_status, name='bulk_update_student_status'),
    path('bulk-activate-by-date/', bulk_activate_by_date_range, name='bulk_activate_by_date_range'),
    path('api/get-deactivated-count/', get_deactivated_students_count, name='get_deactivated_count'),
    
    path('logout-all-users/', logout_all_users, name='logout_all_users'),
    path('api/force-logout-all/', force_logout_all_users, name='force_logout_all'),
    path('api/user-stats/', get_user_stats, name='get_user_stats'),
    
    path('upload-student-status-excel/', upload_student_status_excel, name='upload_student_status_excel'),
    path('download-status-template/', download_student_status_template, name='download_status_template'),
    path('download-status-report/', get_student_status_report, name='download_status_report'),
    
    #Id_card
    path('id-card-generator/', id_card_generator, name='id_card_generator'),
    path('get-students-for-id-card/', get_students_for_id_card, name='get_students_for_id_card'),
    path('generate-id-card-pdf/', generate_id_card_pdf, name='generate_id_card_pdf'),
    path('get-id-card-preview/', get_id_card_preview, name='get_id_card_preview'),
    
    #spin
    path('spin-form/', spin_form, name='spin_form'),
    path('spin-wheel/', spin_wheel, name='spin_wheel'),
    path('get-result/', get_result, name='get_result'),
    path('download-all-spins/', download_all_spin_entries, name='download_all_spins'),
    path('spin-download-page/', spin_download_page, name='spin_download_page'),

]
