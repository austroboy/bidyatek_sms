from django.urls import path
from .views import *

urlpatterns = [
    
    #Accounting Management
    path('accounting/ledger/create/', create_ledger, name='ledger_create'),
    path('accounting/ledger/delete/<int:ledger_id>/', delete_ledger, name='delete_ledger'),
    path('accounting/ledgers/', ledger_list, name='ledger_list'),
    path('accounting/ledger-entries/', ledger_entry_list, name='ledger_entry_list'),
    path('accounting/ledger-entry/create/', create_ledger_entry, name='ledger_entry_create'),
    path('accounting/ledger-entry/delete/<int:entry_id>/', delete_ledger_entry, name='ledger_entry_delete'),
    path('accounting/receive/', receive_management, name='receive_management'),
    path('accounting/receive/delete/<int:receive_id>/', delete_receive, name='delete_receive'),
    path('accounting/payment/', payment_management, name='payment_management'),
    path('accounting/journal_entries/', journal_management, name='journal_management'),
    path('accounting/contra/', contra_management, name='contra_management'),

 
    
    #Report Section
    path('accounting_report/cash-summary/', cash_summary, name='cash_summary'),
    path('cash-summary/pdf/', cash_summary_pdf, name='cash_summary_pdf'),
    path('accounting_report/trial-balance/', trial_balance, name='trial_balance'),
    path('accounting_report/balance-sheet/', balance_sheet, name='balance_sheet'),
    path('balance-sheet/pdf/', balance_sheet_pdf, name='balance_sheet_pdf'),
    path("accounting_report/income_statement/", income_statement, name="income_statement"),
    path('income-statement/pdf/', income_statement_pdf, name='income_statement_pdf'),
    path('accounting_report/voucher-list/', voucher_list, name='voucher_list'),
    path('voucher-list/pdf/', voucher_list_pdf, name='voucher_list_pdf'),
    path('accounting_report/journal-report/', journal_report, name='journal_report'),
    path('journal-report/pdf/', journal_report_pdf, name='journal_report_pdf'),
    path('accounting_report/funds-flow/', funds_flow_report, name='funds_flow_report'),
    path('funds-flow-report/pdf/', funds_flow_report_pdf, name='funds_flow_report_pdf'),
    path('accounting_report/cash-book/', cash_book, name='cash_book'),
    path("accounting_report/bank-book/", bank_book, name="bank_book"),
    path('accounting_report/ledger-summary/', ledger_summary, name='ledger_summary'),
    path('ledger-summary/pdf/', ledger_summary_pdf, name='ledger_summary_pdf'),
    path('accounting_report/category-summary/', category_summary, name='category_summary'),
    path("accounting_report/outstanding-receivables/", outstanding_receivables, name="outstanding_receivables"),
    path("accounting_report/payment-summary/", payment_summary, name="payment_summary"),
    path('accounting_report/ledger-book/', ledger_book, name='ledger_book'),
    path('expense-ledger-report/', expense_report, name='expense_report'),
    path('expense-ledger-report/pdf/', expense_report_pdf, name='expense_report_pdf'),
    path('income-ledger-report/', income_report, name='income_report'),
    path('income-ledger-report/pdf/', income_report_pdf, name='income_report_pdf'),
    
    
    path('reports/fee/', fee_report, name='fee_report'),
    path('fee-report-ui/', fee_report_ui, name='fee_report_ui'),
    path('voucher-report/', voucher_report, name='voucher_report'),
    
    path('student-fee-report/', student_fee_report, name='student_fee_report'),
    path('generate-student-fee-report/', generate_student_fee_report, name='generate_student_fee_report'),

]
