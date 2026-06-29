from django.urls import path
from .views import *
from .api_views import StudentResultByAcademicYearView

urlpatterns = [

    #api view
    path('results/<int:student_id>/<int:academic_year_id>/', StudentResultByAcademicYearView.as_view(), name='student_results_academic_year'),
    
    path('exam/examname/',examname,name='examname'),
    path('addexamname/',add_examname,name='addexamname'),
    path('exam<int:pk>/edit',edit_examname,name='editexamname'),
    path('exam<int:pk>/del',del_examname,name='delexamname'),
    path('listexamname/',list_examname,name='listexamname'),


    path('exam/syllabus/',syllabus,name='syllabus' ),
    path('addsyllabus/',add_syllabus,name='addsyllabus' ),
    path('slbs/<int:pk>/edit',edit_syllabus,name='editsyllabus'),
    path('slbs/<int:pk>/del',del_syllabus,name='delsyllabus'),
    path('listsyllabus/',list_syllabus,name='listsyllabus' ),

      
    path('exam/grade/',grade,name='grade'), 
    path('addgrade/',add_grade,name='addgrade' ),
    path('grade/<int:pk>/edit',edit_grade,name='editgrade'),
    path('grade/<int:pk>/del',del_grade,name='delgrade'),
    path('listgrade/',list_grade,name='listgrade' ), 

    # Schedule   path
    # path('exam/schedule/',schedule,name='schedule'),
    # path('addschedule/',add_schedule,name='addschedule' ),
    # path('sdle/<int:pk>/edit',edit_schedule,name='editschedule'),
    path('sdle/<int:pk>/del',del_schedule,name='delschedule'),
    path('exam/listschedule/',list_schedule,name='listschedule' ),
    path('exam/exam_schedule/',exam_schedule,name='exam_schedule' ),
    path('exam/listschedule/create_schedule/<int:class_name>/', create_schedule, name='create_schedule'),

    path('exam/admit_card/admit_card_without_routine/',admit_card_without_routine,name='admit_card_without_routine' ),
    path('exam/admit_card/admit_card_with_routine/',admit_card_with_routine,name='admit_card_with_routine' ),
    path('exam/seatplan/',seatplan,name='seatplan' ),
    path('exam/mark_blank_sheet/',mark_blank_sheet,name='mark_blank_sheet' ),
    path('exam/exam_signature_sheet/',exam_signature_sheet,name='exam_signature_sheet' ),
    path('exam/exam_fee_sheet/',exam_fee_sheet,name='exam_fee_sheet' ),
    path('exam/oral_mark_sheet/',oral_mark_sheet,name='oral_mark_sheet' ),

    path('get_class_subjects/', get_class_subjects, name='get_class_subjects'), #for mark_list
    path('get_subject_name/', get_subject_name, name='get_subject_name'), #for result_summary
    path('get_mark_subjects/', get_mark_subjects, name='get_mark_subjects'),
    path('result/mark_list/',mark_list,name='mark_list' ),
    path('result/tabulation_sheet/wide_tabulation_sheet/',wide_tabulation_sheet,name='wide_tabulation_sheet' ),
    path('result/tabulation_sheet/narrow_tabulation_report/',narrow_tabulation_report,name='narrow_tabulation_report' ),
    path('result/merit_list/',merit_list,name='merit_list' ),
    path('result/progress_report/',progress_report,name='progress_report' ),
    path('result/progress-report-pdf/', progress_report_pdf, name='progress_report_pdf'),
    path('result/result_summary/',result_sms,name='result_summary' ),
    path('result/list_certificate/', list_certificate, name='list_certificate'),
    path('generate_certificate_report/<int:student_id>/', generate_certificate_report, name='generate_certificate_report'),

    path('api/marksheet/<int:roll_no>/', student_marksheet_api, name='student_marksheet_api'),
    path('result/result_overview/', result_overview, name='result_overview'),
    path('download-result-report/', download_result_report_pdf, name='download_result_report_pdf'),
    path('paginated_report/', paginated_report, name='paginated_report'),
    path('result/subject_wise_analysis/', subject_wise_analysis, name='subject_wise_analysis'),
    path('subject_analysis/download_pdf/', download_subject_analysis_pdf, name='download_subject_analysis_pdf'),
    path('result/top-last-students/', top_last_students_report, name='top_last_students_report'),
    path('result/top-last-students/download-pdf/', download_top_last_pdf, name='download_top_last_pdf'),
    path('result/subject-wise-fail/', subject_wise_fail_report, name='subject_wise_fail_report'),
    path('result/subject-wise-fail/download-pdf/', download_subject_fail_pdf, name='download_subject_fail_pdf'),
    path('tabulation-sheet-two/', tabulation_sheet_two, name='tabulation_sheet_two'),
    path('tabulation-pdf/', tabulation_pdf, name='tabulation_pdf'),
    
    
    path('admit-cards/download/', generate_admit_cards, name='download_admit_cards'),
]