from django.urls import path
from .views import *
from .api_view import *
from django.contrib import admin
from django.urls import path, include
from crucial.admin import admin_site 



urlpatterns = [
    #api route
    path('fees/<int:student_id>/', StudentFeesView.as_view(), name='student_fees'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('fees/unpaid/<int:student_id>/', StudentUnpaidFeesView.as_view(), name='student_unpaid_fees'),
    path('homework/<int:class_id>/', HomeworkByClassView.as_view(), name='homework_by_class'),
    # path('classroutine/routine/',routine,name='routine' ),
    path('classroutine/list_routine/create_routine/<int:class_config_id>/', create_routine, name='create_routine'),
    path('routine/<int:pk>/del',del_routine,name='del_routine'),
    path('classroutine/list_routine/',list_routine,name='list_routine' ),
    path('classroutine/search_teacher/',search_teacher,name='search_teacher' ),
    path('classroutine/search_class/',search_class,name='search_class' ),
    path('get_routinelist/<int:class_id>',get_routinelist,name='get_routinelist' ),
    path('teacher_routinelist/<int:teacher_id>',teacher_routinelist,name='teacher_routinelist' ),
    path('get_existing_routines/', get_existing_routines, name='get_existing_routines'),


    path('site_settings/notice/',notice,name='notice' ), 
    path('add_notice/',add_notice,name='add_notice' ),
    path('notice/<int:pk>/edit',edit_notice,name='edit_notice'),
    path('notice/<int:pk>/del',del_notice,name='del_notice'),
    path('list_notice/',list_notice,name='list_notice' ),

    path('comunication/notification/',notification,name='notification' ),
    path('add_notification/',add_notification,name='add_notification' ),
    path('notification/<int:pk>/edit',edit_notification,name='edit_notification'),
    path('notnotificationice/<int:pk>/del',del_notice,name='del_notification'),
    path('list_notification/',list_notification,name='list_notification' ),

    path('comunication/sms/',sms,name='sms' ),
    path('update_notification_status/<int:sms_id>/', update_notification_status, name='update_notification_status'),
    path('update_notification_body/', update_notification_body, name='update_notification_body'),
    path('comunication/notification_sms/',notification_sms,name='notification_sms' ),
    path('sms/<int:pk>/del',del_sms,name='del_sms'),
    path('sms_report/send_summary/',send_summary,name='send_summary' ),
    path('sms_report/purchase_history/',purchase_history,name='purchase_history' ),
    path('sms_report/sms_delivery/',sms_delivery,name='sms_delivery' ),

    path('fees/fees_head/',fees_head,name='fees_head'),
    path('list_fees_head/',list_fees_head,name='list_fees_head'),
    path('add_fees_head/',add_fees_head,name='add_fees_head'), 
    path('fees_head/<int:pk>/edit',edit_fees_head,name='edit_fees_head'),
    path('fees_head/<int:pk>/del',del_fees_head,name='del_fees_head'),

    path('fees/feepackage/', feepackage,name='feepackage'),
    path('add_feepackage/',add_feepackage,name='add_feepackage' ),
    path('fee/<int:pk>/edit',edit_feepackage,name='edit_feepackage'),
    path('fee/<int:pk>/del',del_feepackage,name='del_feepackage'),
    path('list_feepackage/',list_feepackage,name='list_feepackage' ),

    path('fees/feetype/', feetype,name='feetype'),
    path('addfeetype/',add_feetype,name='addfeetype' ),
    path('feetype/<int:pk>/edit',edit_feetype,name='editfeetype'),
    path('feetype/<int:pk>/del',del_feetype,name='delfeetype'),
    path('listfeetype/',list_feetype,name='listfeetype' ),

    path('get_number_of_months/', get_number_of_months, name='get_number_of_months'),
    path('get_existing_fees/', get_existing_fees, name='get_existing_fees'),
    path('fees/fees_master/',fees_master,name='fees_master' ),

    path('fees/student_fee/',student_fee,name='student_fee' ),
    path('generate_multiple_invoice/',generate_multiple_invoice,name='generate_multiple_invoice' ),
    path('collect-fees/', collect_fees, name='collect_fees'),
    
    path('student/waiver/',waiver,name='waiver' ),
    path('edit_waiver/<int:id>',edit_waiver,name='edit_waiver'),
    path('wai/<int:pk>/del',del_waiver,name='del_waiver'),

    path('fees/addfee/',add_fee,name='addfee'),
    path('fees/listfee/',listfeestatus,name='listfee'),
    path('feestatus/',feestatus,name='feestatus'),
    path('fees/put_back_fee/',put_back_fee,name='put_back_fee'),
    path('fee_put_back/',fee_put_back,name='fee_put_back'),
    path('fees/del_fee/',del_fee,name='del_fee'),
    path('fee_del/',fee_del,name='fee_del'),
    path('student_search/',student_search,name='student_search'),
    path('fees/showfee/',showfee,name='showfee'),
    
    path('fees_report/duefee/',duefee,name='duefee'),
    # path('export-due-fees/', export_due_fees, name='export_due_fees'),
    path('export-due-fees/', export_due_fees, name='export_due_fees'),
    path('fees_report/student_date_fee_report/',student_date_fee_report,name='student_date_fee_report'),
    path('fees_report/student_time_fee_report/',student_time_fee_report,name='student_time_fee_report'),
    path('fees_report/fee_type_wise_report/',fee_type_wise_report,name='fee_type_wise_report'),
    path('fees_report/fee_type_wise_class_report/',fee_type_wise_class_report,name='fee_type_wise_class_report'),

    path('generate_fee_report/<int:fee_id>/', generate_fee_report, name='generate_fee_report'),

    path('service/hostel/packagetype/', packagetype,name='packagetype'),
    path('add_package_type/',add_package_type,name='add_package_type' ),
    path('hostel/<int:pk>/edit',edit_package_type,name='edit_package_type'),
    path('hostel/<int:pk>/del',del_package_type,name='del_package_type'),
    path('list_package_type/',list_package_type,name='list_package_type' ),

    path('service/hostel/hostel_package_allocate/',hostel_package_allocate,name='hostel_package_allocate' ),
    path('update_hostel_package/',update_hostel_package,name='update_hostel_package' ),


    path('service/tution/tution_packagetype/', tution_packagetype,name='tution_packagetype'),
    path('add_tution_package_type/',add_tution_package_type,name='add_tution_package_type' ),
    path('tution/<int:pk>/edit',edit_tution_package_type,name='edit_tution_package_type'),
    path('tution/<int:pk>/del',del_tution_package_type,name='del_tution_package_type'),
    path('list_tution_package_type/',list_tution_package_type,name='list_tution_package_type' ),

    path('service/tution/tution_package_allocate/',tution_package_allocate,name='tution_package_allocate' ),
    path('update_tution_package/', update_tution_package ,name='update_tution_package' ),


    path('service/transport/transport_packagetype/', transport_packagetype,name='transport_packagetype'),
    path('add_transport_package_type/',add_transport_package_type,name='add_transport_package_type' ),
    path('transport/<int:pk>/edit',edit_transport_package_type,name='edit_transport_package_type'),
    path('transport/<int:pk>/del',del_transport_package_type,name='del_transport_package_type'),
    path('list_transport_package_type/',list_transport_package_type,name='list_transport_package_type' ),

    path('service/transport/transport_package_allocate/',transport_package_allocate,name='transport_package_allocate' ),
    path('update_transport_package/', update_transport_package ,name='update_transport_package' ),


    path('expense/expensetype/', expensetype ,name='expensetype'),
    path('addexpensetype/',add_expensetype,name='addexpensetype' ),
    path('expense/<int:pk>/edit',edit_expensetype,name='editexpensetype'),
    path('expense/<int:pk>/del',del_expensetype,name='delexpensetype'),
    path('listexpensetype/',list_expensetype,name='listexpensetype' ),
    

    path('expense/expenseitem/', expenseitem ,name='expenseitem'),
    path('addexpenseitem/',add_expenseitem,name='addexpenseitem' ),
    path('expenseitem/<int:pk>/edit',edit_expenseitem,name='editexpenseitem'),
    path('expenseitem/<int:pk>/del',del_expenseitem,name='delexpenseitem'),
    path('listexpenseitem/',list_expenseitem,name='listexpenseitem' ),
    
    path('expense/search_entry_expense/',search_entry_expense,name='search_entry_expense' ),


    path('income/incomehead/', incomehead ,name='incomehead'),
    path('add_incomehead/',add_incomehead,name='add_incomehead' ),
    path('income/<int:pk>/edit',edit_incomehead,name='edit_incomehead'),
    path('income/<int:pk>/del',del_incomehead,name='del_incomehead'),
    path('list_incomehead/',list_incomehead,name='list_incomehead' ),
    path('income/search_entry_income/',search_entry_income,name='search_entry_income' ),
    

    path('income/incomeitem/', incomeitem ,name='incomeitem'),
    path('add_incomeitem/',add_incomeitem,name='add_incomeitem' ),
    path('incomeitem/<int:pk>/edit',edit_incomeitem,name='edit_incomeitem'),
    path('incomeitem/<int:pk>/del',del_incomeitem,name='del_incomeitem'),
    path('list_incomeitem/',list_incomeitem,name='list_incomeitem' ),

    path('withdraw/withdraw_item/', withdraw ,name='withdraw'),
    path('add_withdraw/',add_withdraw,name='add_withdraw' ),
    path('withdraw/<int:pk>/edit',edit_withdraw,name='edit_withdraw'),
    path('withdraw/<int:pk>/del',del_withdraw,name='del_withdraw'),
    path('list_withdraw/',list_withdraw,name='list_withdraw' ),
    

    path('accounting/search_date_range_income/',search_date_range_income,name='search_date_range_income' ),
    path('accounting/search_head_income/',search_head_income,name='search_head_income' ),
    path('accounting/search_date_range_expense/',search_date_range_expense,name='search_date_range_expense' ),
    path('accounting/search_head_expense/',search_head_expense,name='search_head_expense' ),
    path('accounting/search_date_range_withdraw/',search_date_range_withdraw,name='search_date_range_withdraw' ),
    path('accounting/account_statement/',account_statement,name='account_statement' ),

    path('payroll/addition/',addition,name='addition'),
    path('list_addition/',list_addition,name='list_addition'),
    path('add_addition/',add_addition,name='add_addition'),
    path('addition/<int:pk>/edit',edit_addition,name='edit_addition'),
    path('addition/<int:pk>/del',del_addition,name='del_addition'),


    path('payroll/deduction/',deduction,name='deduction'),
    path('list_deduction/',list_deduction,name='list_deduction'),
    path('add_deduction/',add_deduction,name='add_deduction'), 
    path('deduction/<int:pk>/edit',edit_deduction,name='edit_deduction'),
    path('deduction/<int:pk>/del',del_deduction,name='del_deduction'),


    path('payroll/salary_config/',salary_config,name='salary_config'),
    path('update_salary/',update_salary,name='update_salary'),
    # path('list_salary_config/',list_salary_config,name='list_salary_config'),
    # path('add_salary_config/',add_salary_config,name='add_salary_config'),
    # path('salary_config/<int:pk>/edit',edit_salary_config,name='edit_salary_config'),
    # path('salary_config/<int:pk>/del',del_salary_config,name='del_salary_config'),
    

    path('payroll/salary_increment/',salary_increment,name='salary_increment'),
    path('list_salary_increment/',list_salary_increment,name='list_salary_increment'),
    path('add_salary_increment/',add_salary_increment,name='add_salary_increment'), 
    path('salary_increment/<int:pk>/edit',edit_salary_increment,name='edit_salary_increment'),
    path('salary_increment/<int:pk>/del',del_salary_increment,name='del_salary_increment'),

    path('payroll/salary_allocation/',salary_allocation,name='salary_allocation'), 
    path('payroll/salary_process/',salary_process,name='salary_process'), 
    path('employee_salary/',employee_salary,name='employee_salary'), 
    path('generate_pay_report/<int:salary_id>/', generate_pay_report, name='generate_pay_report'),


    path('homework/',homework,name='homework' ),
    path('add_homework/',add_homework,name='add_homework' ),
    path('hw/<int:pk>/edit',edit_homework,name='edit_homework'),
    path('hw/<int:pk>/del',del_homework,name='del_homework'),
    path('list_homework/',list_homework,name='list_homework' ),

    path('study_material/',add_download,name='study_material' ),
    path('del_download/<int:pk>/del',del_download,name='del_download'),

     
    # Fee Head Ledger Config URLs
    path('fees/fees_head_ledger_config/', fees_head_ledger_config ,name='fees_head_ledger_config'),
    path('add_fees_head_ledger_config/',add_fees_head_ledger_config,name='add_fees_head_ledger_config' ),
    path('fhlc/<int:pk>/edit',edit_fees_head_ledger_config,name='edit_fees_head_ledger_config'),
    path('fhlc/<int:pk>/del',del_fees_head_ledger_config,name='del_fees_head_ledger_config'),
    path('list_fees_head_ledger_config/',list_fees_head_ledger_config,name='list_fees_head_ledger_config' ),

    #Tax
    path('tax-summary/', tax_summary, name='tax_summary'),
    path('tax-detail/<int:profile_id>/', tax_detail, name='tax_detail'),
    
    
    path('bulk-upload-unpaid/', bulk_upload_unpaid_fees, name='bulk_upload_unpaid'),
    
    path('fees/fee_edit/', search_and_edit_fee, name='search_and_edit_fee'),
    path('fees-report/', fees_collection_report, name='fees_report'),
    path('fees-report/pdf/', fees_collection_report_pdf, name='fees_collection_report_pdf'),
    path('fees-report/excel/', fees_collection_report_excel, name='fees_collection_report_excel'),
    path('previous-dues/', previous_dues_report, name='previous_dues_report'),
    path('download-previous-dues-pdf/', download_previous_dues_pdf, name='download_previous_dues_pdf'),
    path('master-head-wise-report/', master_head_wise_report, name='master_head_wise_report'),
    path('master-head-wise-report/pdf/', download_pdf, name='download_pdf'),
    path('master-head-wise-report/excel/', download_excel, name='download_excel'),
    path('previous-software-due-report/', previous_software_due_report, name='previous_software_due_report'),
    path('download-previous-due-pdf/', download_previous_due_pdf, name='download_previous_due_pdf'),
    
    path('fee-reports/', fee_reports, name='fee_reports'),
    path('check-report/', check_report_status, name='check-report-status'),
    path('serve-pdf/', serve_generated_pdf, name='serve-pdf'),
    path('date-reports/', feedate_reports, name='fee_date_reports'),
    path('export-fees/', export_fees_to_excel, name='export_fees_to_excel'),
    
    
    path('update-fee-type/', update_fee_type, name='update_fee_type'),
    path('admin/', admin_site.urls),
    path('fees/list/', fees_list, name='fees_list'),
    path('fees/transfer/', transfer_fees, name='transfer_fees'),
    
    path('duplicate-fees/', duplicate_fees_list, name='duplicate_fees_list'),
    path('delete-duplicate-fee/<int:fee_id>/', delete_duplicate_fee, name='delete_duplicate_fee'),
    
    path('find-duplicates/', find_duplicate_fees, name='find_duplicate_fees'),
    path('delete-fee/<int:fee_id>/', delete_fee_entry, name='delete_fee_entry'),
    
    path('manage-fees/', manage_fees, name='manage_fees'),
    
    
    
    path('master_head_report/', master_head_wise_report_two, name='master_head_report'),
    path('download_master_head_pdf/', download_pdf_two, name='download_master_head_pdf'),
    path('download-excel-two/', download_excel_two, name='download_excel_two'),
    path('new-fees-report/', new_fees_collection_report, name='new_fees_report'),
    path('new-fees-report-pdf/', new_fees_collection_report_pdf, name='new_fees_report_pdf'),
    path('student-fees-report/', student_fees_report, name='student_fees_report'),
    path('student-fees-report/pdf/', student_fees_report_pdf, name='student_fees_report_pdf'),
    path('student-fees-report/excel/', student_fees_report_excel, name='student_fees_report_excel'),
    
    path('hostel-fees-report/', hostel_fees_report, name='hostel_fees_report'),
    path('download/', download_success_transactions_excel, name='download_excel'),
    path('download-student-payments/', download_receive_excel, name='download_student_payments'),
    
    
    path('check-task-status/', check_task_status, name='check_task_status'),
    path('download-report/', download_report, name='download_report'),
    path('add-late-fees/', add_late_fees, name='add_late_fees'),
    path('delete-late-fees/', delete_late_fees, name='delete_late_fees'),
    
    path('student-head-report/', student_head_report, name='student_head_report'),
    path('student-head-report/pdf/', student_head_report_pdf, name='student_head_report_pdf'),
    path('student-head-report/excel/', student_head_report_excel, name='student_head_report_excel'),
    
    path('admit-cards/download/', admit_card_download_view, name='admit_card_download'),
    path('admit-card/bulk/', bulk_admit_card_download, name='bulk_admit_card_download'),
    path('admit-card/single/', single_admit_card_download, name='single_admit_card_download'),
    path('admit-card/download/<int:student_id>/', download_student_admit_card, name='download_student_admit_card'),
    
    path('fee-report/', fee_report, name='fee_report'),
    path('fee_bulk_upload/', fee_bulk_upload, name='fee_bulk_upload'),
    
    path('deposit-form/', deposit_form_ui, name='deposit_form_ui'),
    path('deposit-form/pdf/<int:student_id>/', generate_deposit_pdf, name='generate_deposit_pdf'),
    
    path('download-fee-data/', download_fee_data, name='download_fee_data'),
    
    path('fees-management/', fees_management_view, name='fees_management'),
    path('download-exam-half-november/', download_exam_half_november_fees, name='download_exam_half_november'),
    path('delete-exam-half-november/', delete_exam_half_november_fees, name='delete_exam_half_november'),
    
    path('finance/upload-fee-payments/', upload_fee_payments, name='upload_fee_payments'), 
    path('finance/download-sample-excel/', download_sample_excel,  name='download_sample_excel'),

]