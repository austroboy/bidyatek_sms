from django.urls import path
from .views import *
from .api_views import *

urlpatterns = [
    path('', dashboard ,name='dashboard' ),
    path('login/', auth_login ,name='login' ),
    path('logout/', logoutPage, name='logout'),
    path('change_password/', change_password, name='change_password'),
    path('settings/basic_setup/',crud_basic,name='basic_setup' ),

     # class path
    
  
    path('<int:pk>/edit/', edit_classname, name='editclassname'),
    path('<int:pk>/del/',del_classname,name='delclassname'),
    path('listclassname/',list_classname,name='listclassname' ),
 

    # section path
 
    path('section/<int:pk>/edit',edit_sectionname,name='editsection'),
    path('section/<int:pk>/del',del_sectionname,name='delsection'),
    path('listsectionname/',list_sectionname,name='listsection' ),

    # group path
 
    path('group/<int:pk>/edit',edit_groupname,name='editgroup'),
    path('group/<int:pk>/del',del_groupname,name='delgroup'),
    path('listgroupname/',list_groupname,name='listgroup' ),

    # subject path
    
    path('subject/<int:pk>/edit',edit_subjectname,name='editsubjectname'),
    path('subject/<int:pk>/del',del_subjectname,name='delsubjectname'),
    path('listsubjectname/',list_subjectname,name='listsubjectname' ),

    # shift path
    
    path('shift/<int:pk>/edit',edit_shift,name='edit_shift'),
    path('shift/<int:pk>/del',del_shift,name='del_shift'),
    path('list_shiftname/',list_shiftname,name='list_shiftname' ),

     # period path
    
    path('period/<int:pk>/edit',edit_periodname,name='edit_periodname'),
    path('period/<int:pk>/del',del_periodname,name='del_periodname'),
    path('list_periodname/',list_periodname,name='list_periodname' ),
     # role path
    
    path('role/<int:pk>/edit',edit_roletype,name='edit_roletype'),
    path('role/<int:pk>/del',del_roletype,name='del_roletype'),
    path('list_roletype/',list_roletype,name='list_roletype' ),

    # Marktype path
    
    path('marktype/<int:pk>/edit',edit_marktype,name='edit_marktype'),
    path('marktype/<int:pk>/del',del_marktype,name='del_marktype'),
    path('list_marktype/',list_marktype,name='list_marktype' ),

     # addmission_session path
    
    path('session/<int:pk>/edit',edit_addmission_session,name='edit_addmission_session'),
    path('session/<int:pk>/del',del_addmission_session,name='del_addmission_session'),
    path('list_addmission_session/',list_addmission_session,name='list_addmission_session' ),
    path('set_academic_year/',set_academic_year,name='set_academic_year' ),

    # ClassConfig name

    # path('settings//list_class_config/create_class_config/<int:class_id>/', create_class_config, name='create_class_config'),
    # path('config/<int:pk>/del',del_class_config,name='del_class_config'),
    path('settings/list_class_config/',list_class_config,name='list_class_config' ),
    path('edit-class-group-config/<int:pk>/', get_class_group_config, name='edit_class_group_config'),
    path('update-class-group-config/<int:pk>/', update_class_group_config, name='update_class_group_config'),
    path('edit-class-config/<int:pk>/', get_class_config, name='edit_class_config'),
    path('update-class-config/<int:pk>/', update_class_config, name='update_class_config'),
    path('delete-class-config/<int:pk>/', delete_class_config, name='delete_class_config'),
    path('delete-class-group-config/<int:pk>/', delete_class_group_config, name='delete_class_group_config'),

    # PeriodConfig name

    path('settings/period_config/',period_config,name='period_config' ), 

    

    path('settings/create_subject_assign/', create_subject_assign, name='create_subject_assign'),
    path('get_subject_assign/<int:class_id>', get_subject_assign, name='get_subject_assign'),
    path('settings/create_teacher_assign/', create_teacher_assign, name='create_teacher_assign'),
    path('get_teacher_assign/<int:teacher_id>/', get_teacher_assign, name='get_teacher_assign'),

    path('settings/choosable_subject/',choosable_subject,name='choosable_subject' ),
    path('get_choosable_subject/<int:student_id>/', get_choosable_subject, name='get_choosable_subject'),



    path('settings/list_subject_conf/',list_subject_conf,name='list_subject_conf' ),
    path('settings/list_subject_conf/create_subject_conf/<int:studentclass>', create_subject_conf, name='create_subject_conf'),
    path('subject_conf/<int:pk>/del',del_subject_conf,name='del_subject_conf'),


    path('settings/list_mark_config/',list_mark_config,name='list_mark_config' ),
    path('settings/list_mark_config/create_mark_conf/<int:studentclass>/', create_mark_conf, name='create_mark_conf'),
    path('mark_conf/<int:pk>/del',del_mark_conf,name='del_mark_conf'), 

    path("settings/submit_mark_config/", submit_mark_config, name="submit_mark_config"),

    path('admission-years/', AdmissionYearListAPIView.as_view(), name='admission-year-list'),
    path('academic-sessions/', AcademicSessionListAPIView.as_view(), name='academic-session-list'),
    path('class-configs/', ClassConfigListAPIView.as_view(), name='class-config-list'),
    path('check-class-group/<int:class_id>/', check_class_group, name='check_class_group'),


] 