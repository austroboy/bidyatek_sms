# # crucial/tasks.py
# from celery import shared_task
# from django.template.loader import render_to_string
# from weasyprint import HTML
# from django.core.files.storage import default_storage
# from django.core.cache import cache
# import logging
# from django.db import connection

# logger = logging.getLogger(__name__)

# @shared_task(bind=True)
# def generate_pdf_report_task(self, params):
#     try:
#         from .models import (
#             StudentProfile, Fee_month,
#             StudentClass, StuGroup
#         )
#         from core.models import StudentSection
#         from django.core.exceptions import ObjectDoesNotExist
#         import logging
#         logger = logging.getLogger(__name__)

#         context = {}
#         data = params.get('context_data', {})
        
#         context['status'] = data.get('status')
#         context['version'] = data.get('version')

#         try:
#             if data.get('month_id'):
#                 context['month'] = Fee_month.objects.get(id=data['month_id'])
#             if data.get('class_id'):
#                 context['class'] = StudentClass.objects.get(id=data['class_id'])
#             if data.get('section_id'):
#                 context['section'] = StudentSection.objects.get(id=data['section_id'])
#             if data.get('group_id'):
#                 context['group'] = StuGroup.objects.get(id=data['group_id'])
#         except ObjectDoesNotExist as e:
#             logger.error(f"Missing object: {str(e)}")
#             raise

#         students = []
#         for item in data.get('student_ids', []):
#             try:
#                 if params.get('status') == 'Paid':
#                     student = StudentProfile.objects.get(id=item)
#                     students.append(student)
#                 else:
#                     student = StudentProfile.objects.get(id=item['student_id'])
#                     students.append({
#                         'student': student,
#                         'total_unpaid': Decimal(str(item['total_unpaid']))
#                     })
#             except ObjectDoesNotExist:
#                 logger.warning(f"Student not found: {item}")
#                 continue

#         context['students'] = students

#         html_string = render_to_string(params['template'], context)
#         html = HTML(string=html_string)
#         pdf = html.write_pdf()

#         file_path = f"reports/{params['filename']}"
#         default_storage.save(file_path, pdf)

#         cache.set(self.request.id, {
#             'status': 'SUCCESS',
#             'file_path': file_path
#         }, 300)

#         return file_path

#     except Exception as e:
#         logger.error(f"Task failed: {str(e)}", exc_info=True)
#         cache.set(self.request.id, {
#             'status': 'FAILURE',
#             'error': str(e)
#         }, 300)
#         raise
    
    
    





# from celery import shared_task
# from django.core.files.storage import default_storage
# from django.template.loader import render_to_string
# from weasyprint import HTML, CSS
# import xlsxwriter
# import pandas as pd
# from io import BytesIO

# @shared_task
# def generate_pdf_report(task_id, get_params):
#     from .models import ReportTask  # Import inside task to avoid circular import
    
#     try:
#         # Simulate request object
#         class MockRequest:
#             GET = get_params
#             def build_absolute_uri(self, path):
#                 return f'http://example.com{path}'
        
#         context = generate_student_fees_context(MockRequest())
        
#         # PDF generation code from your view
#         html = render_to_string('crucial/report/student_fees_report_pdf.html', context)
#         output = BytesIO()
        
#         HTML(string=html).write_pdf(output, stylesheets=[
#         CSS(string='''
#             /* Table structure enforcement */
#             .styled-table {
#                 table-layout: fixed !important;
#                 border-collapse: collapse !important;
#                 width: 100% !important;
#             }

#             /* Default column sizing */
#             .styled-table th,
#             .styled-table td {
#                 width: auto !important;
#                 min-width: 40px !important;
#                 padding: 2px !important;
#                 overflow: hidden !important;
#                 text-overflow: ellipsis !important;
#             }

#             /* Narrow columns: 1(SL), 4(Roll), 5(Class), 6(Group), 7(Section), 8(Shift) */
#             .styled-table th:nth-child(1),
#             .styled-table th:nth-child(4),
#             .styled-table th:nth-child(5),
#             .styled-table th:nth-child(6),
#             .styled-table th:nth-child(7),
#             .styled-table th:nth-child(8),
#             .styled-table td:nth-child(1),
#             .styled-table td:nth-child(4),
#             .styled-table td:nth-child(5),
#             .styled-table td:nth-child(6),
#             .styled-table td:nth-child(7),
#             .styled-table td:nth-child(8) {
#                 width: 20px !important;  /* Increased from 7px for better visibility */
#                 min-width: 20px !important;
#                 max-width: 20px !important;
#             }

#             /* Wide columns: Student(2-3), Version(9) */
#             .styled-table th:nth-child(2),
#             .styled-table th:nth-child(3),
#             .styled-table th:nth-child(9),
#             .styled-table td:nth-child(2),
#             .styled-table td:nth-child(3),
#             .styled-table td:nth-child(9) {
#                 min-width: 60px !important;
#                 max-width: 120px !important;
#             }

#             /* Vertical header adjustments */
#             .vertical-header {
#                 position: absolute !important;
#                 bottom: 8px !important;
#                 left: 50% !important;
#                 transform: translateX(-50%) rotate(-90deg) !important;
#                 transform-origin: center !important;
#                 width: 80px !important;
#                 font-size: 8px !important;
#                 line-height: 1.2 !important;
#                 text-align: center !important;
#                 padding: 0 !important;
#                 margin: 0 !important;
#             }

#             /* Student name column specific */
#             td:nth-child(2) {
#                 text-align: left !important;
#                 padding-left: 4px !important;
#             }

#             .styled-table th {
#                 height: 155px !important;
#                 padding: 0 !important;
#                 position: relative !important;
#             }

#             /* Page break handling */
#             .page-break {
#                 page-break-inside: avoid !important;
#             }

#             @media print {
#                 .page-break {
#                     display: block !important;
#                     page-break-before: always !important;
#                 }
#             }
#         ''')
#     ])
        
#         # Save file
#         file_path = f'reports/{task_id}.pdf'
#         default_storage.save(file_path, output)
        
#         ReportTask.objects.filter(task_id=task_id).update(
#             status='SUCCESS',
#             file_path=file_path
#         )
        
#     except Exception as e:
#         ReportTask.objects.filter(task_id=task_id).update(
#             status='FAILURE',
#             error_message=str(e)
#         )

# @shared_task
# def generate_excel_report(task_id, get_params):
#     try:
#         # Mock request for context generation
#         class MockRequest:
#             GET = get_params
#             user = None  # Add user if needed for filtering

#         context = generate_student_fees_context(MockRequest())
#         students_data = context.get('students_data', [])
#         used_fee_heads = context.get('used_fee_heads', [])
#         column_totals = context.get('column_totals', defaultdict(Decimal))
#         grand_total = context.get('grand_total', Decimal('0.00'))
#         other_fee_total = context.get('other_fee_total', Decimal('0.00'))

#         # Columns
#         columns = [
#             'SL NO', 'Student Name', 
#             'Class', 'Group', 'Section', 
#             'Shift', 'Version', 'Roll No'
#         ] + [fh.name for fh in used_fee_heads] + ['Other Fee', 'Total'] 

#         # Data rows
#         data_rows = []
#         for serial_no, student in enumerate(students_data, start=1):
#             row = [
#                 serial_no,
#                 student['student'].student_field.name,
#                 student['class'],
#                 student['group'],
#                 student['section'],
#                 student['shift'],
#                 student['version'],
#                 student['student'].roll_no or '',
#             ] + student['payments'] + [
#                 Decimal('0.00'),
#                 student['total']
#             ]
#             data_rows.append(row)

#         total_row = [
#             'Grand Total', '', '', '', '', '', '', ''
#         ] + [column_totals.get(fh.id, Decimal('0.00')) for fh in used_fee_heads] + [
#             other_fee_total, grand_total
#         ]
#         data_rows.append(total_row)

#         df = pd.DataFrame(data_rows, columns=columns)

#         # Excel writing
#         output = BytesIO()
#         with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#             df.to_excel(writer, sheet_name='Student Fees Report', index=False, startrow=3)
#             workbook = writer.book
#             worksheet = writer.sheets['Student Fees Report']

#             # Formatting
#             thin_border = {'border': 1, 'border_color': '#000000'}
#             thick_top_border = {'top': 2, 'border_color': '#000000'}

#             header_format = workbook.add_format({
#                 **thin_border, 'bold': True, 'text_wrap': True,
#                 'valign': 'top', 'fg_color': '#4F81BD', 'font_color': 'white'
#             })
#             title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
#             currency_format = workbook.add_format({**thin_border, 'num_format': '#,##0.00'})
#             total_format = workbook.add_format({**thin_border, **thick_top_border, 'num_format': '#,##0.00', 'bold': True, 'fg_color': '#D9E1F2'})
#             center_format = workbook.add_format({**thin_border, 'align': 'center'})

#             worksheet.merge_range('A1:Z1', 'STUDENT FEES COLLECTION REPORT', title_format)
#             worksheet.merge_range('A2:Z2', f"Date Range: {context.get('from_date')} to {context.get('to_date')}", workbook.add_format({'align': 'center', 'italic': True}))

#             for col_num, value in enumerate(columns):
#                 worksheet.write(3, col_num, value, header_format)

#             for row_num in range(4, len(data_rows) + 4):
#                 for col_num in range(len(columns)):
#                     cell_value = data_rows[row_num - 4][col_num]
#                     if row_num == len(data_rows) + 3:
#                         if col_num >= 8:
#                             worksheet.write(row_num, col_num, cell_value, total_format)
#                         else:
#                             worksheet.write(row_num, col_num, cell_value, header_format)
#                     else:
#                         if col_num in [0, 2, 3, 4, 5, 6, 7]:
#                             worksheet.write(row_num, col_num, cell_value, center_format)
#                         elif col_num >= 8:
#                             worksheet.write(row_num, col_num, cell_value, currency_format)
#                         else:
#                             worksheet.write(row_num, col_num, cell_value, workbook.add_format(thin_border))

#             for i, col in enumerate(columns):
#                 max_len = max(df[col].astype(str).apply(len).max(), len(str(col)) + 2)
#                 worksheet.set_column(i, i, max_len + 2)

#             worksheet.freeze_panes(4, 2)
#             worksheet.set_zoom(90)
#             worksheet.autofilter(3, 0, 3, len(columns) - 1)
#             worksheet.set_landscape()
#             worksheet.set_margins(left=0.5, right=0.5, top=0.75, bottom=0.75)
#             worksheet.repeat_rows(0, 3)
#             worksheet.print_area(0, 0, len(data_rows) + 3, len(columns) - 1)

#         file_path = f'reports/{task_id}.xlsx'
#         default_storage.save(file_path, output)

#         ReportTask.objects.filter(task_id=task_id).update(
#             status='SUCCESS',
#             file_path=file_path
#         )

#     except Exception as e:
#         ReportTask.objects.filter(task_id=task_id).update(
#             status='FAILURE',
#             error_message=str(e)
#         )
        
        
# from celery import shared_task
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from django.template.loader import render_to_string
# from weasyprint import HTML, CSS
# import xlsxwriter
# import pandas as pd
# from io import BytesIO
# from collections import defaultdict
# from decimal import Decimal

# from .models import ReportTask

# @shared_task
# def generate_pdf_report(task_id, get_params, schema_name):
#     from django_tenants.utils import tenant_context
#     from organizer.models import Tenant

#     try:
#         tenant = Tenant.objects.get(schema_name=schema_name)
#         with tenant_context(tenant):

#             class MockRequest:
#                 GET = get_params
#                 def build_absolute_uri(self, path):
#                     return f'http://example.com{path}'

#             context = generate_student_fees_context(MockRequest())
#             html = render_to_string('crucial/report/student_fees_report_pdf.html', context)
#             output = BytesIO()

#             HTML(string=html).write_pdf(output, stylesheets=[CSS(string='''
#             /* Table structure enforcement */
#             .styled-table {
#                 table-layout: fixed !important;
#                 border-collapse: collapse !important;
#                 width: 100% !important;
#             }

#             /* Default column sizing */
#             .styled-table th,
#             .styled-table td {
#                 width: auto !important;
#                 min-width: 40px !important;
#                 padding: 2px !important;
#                 overflow: hidden !important;
#                 text-overflow: ellipsis !important;
#             }

#             /* Narrow columns: 1(SL), 4(Roll), 5(Class), 6(Group), 7(Section), 8(Shift) */
#             .styled-table th:nth-child(1),
#             .styled-table th:nth-child(4),
#             .styled-table th:nth-child(5),
#             .styled-table th:nth-child(6),
#             .styled-table th:nth-child(7),
#             .styled-table th:nth-child(8),
#             .styled-table td:nth-child(1),
#             .styled-table td:nth-child(4),
#             .styled-table td:nth-child(5),
#             .styled-table td:nth-child(6),
#             .styled-table td:nth-child(7),
#             .styled-table td:nth-child(8) {
#                 width: 20px !important;  /* Increased from 7px for better visibility */
#                 min-width: 20px !important;
#                 max-width: 20px !important;
#             }

#             /* Wide columns: Student(2-3), Version(9) */
#             .styled-table th:nth-child(2),
#             .styled-table th:nth-child(3),
#             .styled-table th:nth-child(9),
#             .styled-table td:nth-child(2),
#             .styled-table td:nth-child(3),
#             .styled-table td:nth-child(9) {
#                 min-width: 60px !important;
#                 max-width: 120px !important;
#             }

#             /* Vertical header adjustments */
#             .vertical-header {
#                 position: absolute !important;
#                 bottom: 8px !important;
#                 left: 50% !important;
#                 transform: translateX(-50%) rotate(-90deg) !important;
#                 transform-origin: center !important;
#                 width: 80px !important;
#                 font-size: 8px !important;
#                 line-height: 1.2 !important;
#                 text-align: center !important;
#                 padding: 0 !important;
#                 margin: 0 !important;
#             }

#             /* Student name column specific */
#             td:nth-child(2) {
#                 text-align: left !important;
#                 padding-left: 4px !important;
#             }

#             .styled-table th {
#                 height: 155px !important;
#                 padding: 0 !important;
#                 position: relative !important;
#             }

#             /* Page break handling */
#             .page-break {
#                 page-break-inside: avoid !important;
#             }

#             @media print {
#                 .page-break {
#                     display: block !important;
#                     page-break-before: always !important;
#                 }
#             }
#         ''')])
#             output.seek(0)

#             file_path = f'reports/{task_id}.pdf'
#             default_storage.save(file_path, ContentFile(output.read()))

#             ReportTask.objects.filter(task_id=task_id).update(
#                 status='SUCCESS',
#                 file_path=file_path
#             )

#     except Exception as e:
#         ReportTask.objects.filter(task_id=task_id).update(
#             status='FAILURE',
#             error_message=str(e)
#         )


# @shared_task
# def generate_excel_report(task_id, get_params, schema_name):
#     from django_tenants.utils import tenant_context
#     from organizer.models import Tenant

#     try:
#         tenant = Tenant.objects.get(schema_name=schema_name)
#         with tenant_context(tenant):

#             class MockRequest:
#                 GET = get_params
#                 user = None

#             context = generate_student_fees_context(MockRequest())
#             students_data = context.get('students_data', [])
#             used_fee_heads = context.get('used_fee_heads', [])
#             column_totals = context.get('column_totals', defaultdict(Decimal))
#             grand_total = context.get('grand_total', Decimal('0.00'))
#             other_fee_total = context.get('other_fee_total', Decimal('0.00'))

#             columns = [
#                 'SL NO', 'Student Name', 
#                 'Class', 'Group', 'Section', 
#                 'Shift', 'Version', 'Roll No'
#             ] + [fh.name for fh in used_fee_heads] + ['Other Fee', 'Total'] 

#             data_rows = []
#             for serial_no, student in enumerate(students_data, start=1):
#                 row = [
#                     serial_no,
#                     student['student'].student_field.name,
#                     student['class'],
#                     student['group'],
#                     student['section'],
#                     student['shift'],
#                     student['version'],
#                     student['student'].roll_no or '',
#                 ] + student['payments'] + [
#                     Decimal('0.00'),
#                     student['total']
#                 ]
#                 data_rows.append(row)

#             total_row = [
#                 'Grand Total', '', '', '', '', '', '', ''
#             ] + [column_totals.get(fh.id, Decimal('0.00')) for fh in used_fee_heads] + [
#                 other_fee_total, grand_total
#             ]
#             data_rows.append(total_row)

#             df = pd.DataFrame(data_rows, columns=columns)

#             output = BytesIO()
#             with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                 df.to_excel(writer, sheet_name='Student Fees Report', index=False, startrow=3)
#                 workbook = writer.book
#                 worksheet = writer.sheets['Student Fees Report']

#                 # Formatting
#                 thin_border = {'border': 1, 'border_color': '#000000'}
#                 thick_top_border = {'top': 2, 'border_color': '#000000'}

#                 header_format = workbook.add_format({
#                     **thin_border, 'bold': True, 'text_wrap': True,
#                     'valign': 'top', 'fg_color': '#4F81BD', 'font_color': 'white'
#                 })
#                 title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
#                 currency_format = workbook.add_format({**thin_border, 'num_format': '#,##0.00'})
#                 total_format = workbook.add_format({**thin_border, **thick_top_border, 'num_format': '#,##0.00', 'bold': True, 'fg_color': '#D9E1F2'})
#                 center_format = workbook.add_format({**thin_border, 'align': 'center'})

#                 worksheet.merge_range('A1:Z1', 'STUDENT FEES COLLECTION REPORT', title_format)
#                 worksheet.merge_range('A2:Z2', f"Date Range: {context.get('from_date')} to {context.get('to_date')}", workbook.add_format({'align': 'center', 'italic': True}))

#                 for col_num, value in enumerate(columns):
#                     worksheet.write(3, col_num, value, header_format)

#                 for row_num in range(4, len(data_rows) + 4):
#                     for col_num in range(len(columns)):
#                         cell_value = data_rows[row_num - 4][col_num]
#                         if row_num == len(data_rows) + 3:
#                             if col_num >= 8:
#                                 worksheet.write(row_num, col_num, cell_value, total_format)
#                             else:
#                                 worksheet.write(row_num, col_num, cell_value, header_format)
#                         else:
#                             if col_num in [0, 2, 3, 4, 5, 6, 7]:
#                                 worksheet.write(row_num, col_num, cell_value, center_format)
#                             elif col_num >= 8:
#                                 worksheet.write(row_num, col_num, cell_value, currency_format)
#                             else:
#                                 worksheet.write(row_num, col_num, cell_value, workbook.add_format(thin_border))

#                 for i, col in enumerate(columns):
#                     max_len = max(df[col].astype(str).apply(len).max(), len(str(col)) + 2)
#                     worksheet.set_column(i, i, max_len + 2)

#                 worksheet.freeze_panes(4, 2)
#                 worksheet.set_zoom(90)
#                 worksheet.autofilter(3, 0, 3, len(columns) - 1)
#                 worksheet.set_landscape()
#                 worksheet.set_margins(left=0.5, right=0.5, top=0.75, bottom=0.75)
#                 worksheet.repeat_rows(0, 3)
#                 worksheet.print_area(0, 0, len(data_rows) + 3, len(columns) - 1)

#             output.seek(0)
#             file_path = f'reports/{task_id}.xlsx'
#             default_storage.save(file_path, ContentFile(output.read()))

#             ReportTask.objects.filter(task_id=task_id).update(
#                 status='SUCCESS',
#                 file_path=file_path
#             )

#     except Exception as e:
#         ReportTask.objects.filter(task_id=task_id).update(
#             status='FAILURE',
#             error_message=str(e)
#         )



import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms.settings')
django.setup()

# tasks.py (add at top)
import sys
if sys.platform == 'win32':
    import pywintypes
    import win32api
    import win32con

    # Fix Windows file locking issues
    def _unlink(name):
        try:
            win32api.SetFileAttributes(name, win32con.FILE_ATTRIBUTE_NORMAL)
            os.unlink(name)
        except pywintypes.error:
            pass

    import shutil
    shutil.rmtree = lambda *args, **kwargs: None



# tasks.py
from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
import xlsxwriter
import pandas as pd
from io import BytesIO
from django.core.files.storage import default_storage
import time
from .utils import generate_student_fees_context

from celery import shared_task
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.test import RequestFactory
from weasyprint import HTML, CSS
from io import BytesIO
from miscellaneous.models import Institute
from core.models import *
from accounting.models import Receive
from user.models import *
from collections import defaultdict
from decimal import Decimal

from django.test import RequestFactory
from django_tenants.utils import schema_context
from django.core.paginator import Page
from django.core.paginator import Paginator

@shared_task
def generate_pdf_report_task(params):
    schema_name = params.get('schema_name')
    
    with schema_context(schema_name):
        # Rest of your existing PDF generation code
        factory = RequestFactory()
        request = factory.get('/dummy-path', {
            'from_date': params.get('from_date'),
            'to_date': params.get('to_date'),
            'class': params.get('class'),
            'section': params.get('section'),
            'group': params.get('group'),
            'shift': params.get('shift'),
            'version': params.get('version')
        })
        
        context = generate_student_fees_context(request)

        # Step 3: Render HTML template
        html = render_to_string(params['template'], context)

        # Step 4: Convert HTML to PDF with custom styles
        pdf = HTML(string=html).write_pdf(stylesheets=[
            CSS(string='''
                .styled-table {
                    table-layout: fixed !important;
                    border-collapse: collapse !important;
                    width: 100% !important;
                }

                .styled-table th,
                .styled-table td {
                    width: auto !important;
                    min-width: 40px !important;
                    padding: 2px !important;
                    overflow: hidden !important;
                    text-overflow: ellipsis !important;
                }

                .styled-table th:nth-child(1),
                .styled-table th:nth-child(4),
                .styled-table th:nth-child(5),
                .styled-table th:nth-child(6),
                .styled-table th:nth-child(7),
                .styled-table th:nth-child(8),
                .styled-table td:nth-child(1),
                .styled-table td:nth-child(4),
                .styled-table td:nth-child(5),
                .styled-table td:nth-child(6),
                .styled-table td:nth-child(7),
                .styled-table td:nth-child(8) {
                    width: 20px !important;
                    min-width: 20px !important;
                    max-width: 20px !important;
                }

                .styled-table th:nth-child(2),
                .styled-table th:nth-child(3),
                .styled-table th:nth-child(9),
                .styled-table td:nth-child(2),
                .styled-table td:nth-child(3),
                .styled-table td:nth-child(9) {
                    min-width: 60px !important;
                    max-width: 120px !important;
                }

                .vertical-header {
                    position: absolute !important;
                    bottom: 8px !important;
                    left: 50% !important;
                    transform: translateX(-50%) rotate(-90deg) !important;
                    transform-origin: center !important;
                    width: 80px !important;
                    font-size: 8px !important;
                    line-height: 1.2 !important;
                    text-align: center !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }

                td:nth-child(2) {
                    text-align: left !important;
                    padding-left: 4px !important;
                }

                .styled-table th {
                    height: 155px !important;
                    padding: 0 !important;
                    position: relative !important;
                }

                .page-break {
                    page-break-inside: avoid !important;
                }

                @media print {
                    .page-break {
                        display: block !important;
                        page-break-before: always !important;
                    }
                }
            ''')
        ])

        # Step 5: Save PDF to storage
        file_path = os.path.join('reports', params["filename"])
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        with open(full_path, 'wb') as f:
            f.write(pdf)
        
        return file_path

from io import BytesIO
import pandas as pd
import xlsxwriter
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, Page
@shared_task
def generate_excel_report_task(params):
    schema_name = params.get('schema_name')

    with schema_context(schema_name):
        try:
            # Create dummy request with ALL original parameters
            factory = RequestFactory()
            clean_params = {k: v for k, v in params.items() if k not in ['filename', 'schema_name']}
            clean_params['for_report'] = '1' 
            request = factory.get('/dummy-path', clean_params)

            # Generate context
            context = generate_student_fees_context(request)

            # Safely extract data from context
            students_data = context.get('students_data', [])
            if hasattr(students_data, 'object_list'):
                students_data = students_data.object_list  
            used_fee_heads = context.get('used_fee_heads', [])
            column_totals = context.get('column_totals', defaultdict(Decimal))
            grand_total = context.get('grand_total', Decimal('0.00'))
            other_fee_total = context.get('other_fee_total', Decimal('0.00'))

            # Prepare columns and data rows
            columns = [
                'SL NO', 'Student Name', 'Class', 'Group', 'Section',
                'Shift', 'Version', 'Roll No'
            ] + [fh.name for fh in used_fee_heads] + ['Other Fee', 'Total']

            data_rows = []
            serial_no = 1
            for student in students_data:
                row = [
                    serial_no,
                    student['student'].student_field.name,
                    student['class'],
                    student['group'],
                    student['section'],
                    student['shift'],
                    student['version'],
                    student['student'].roll_no or '',
                ] + student['payments'] + [
                    Decimal('0.00'),
                    student['total']
                ]
                data_rows.append(row)
                serial_no += 1

            # Add grand total row
            total_row = [
                'Grand Total', '', '', '', '', '', '', ''
            ] + [column_totals.get(fh.id, Decimal('0.00')) for fh in used_fee_heads] + [
                other_fee_total,
                grand_total
            ]
            data_rows.append(total_row)

            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=columns)

            # Generate Excel in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Student Fees Report', index=False, startrow=3)

                workbook = writer.book
                worksheet = writer.sheets['Student Fees Report']

                # Define border styles
                thin_border = {
                    'border': 1,
                    'border_color': '#000000'
                }
                thick_top_border = {
                    'top': 2,
                    'border_color': '#000000'
                }

                # Create formats
                header_format = workbook.add_format({
                    **thin_border,
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#4F81BD',
                    'font_color': 'white'
                })

                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 16,
                    'align': 'center',
                    'valign': 'vcenter'
                })

                currency_format = workbook.add_format({
                    **thin_border,
                    'num_format': '#,##0.00'
                })

                total_format = workbook.add_format({
                    **thin_border,
                    **thick_top_border,
                    'num_format': '#,##0.00',
                    'bold': True,
                    'fg_color': '#D9E1F2'
                })

                center_format = workbook.add_format({
                    **thin_border,
                    'align': 'center'
                })

                # Add titles
                worksheet.merge_range('A1:Z1', 'STUDENT FEES COLLECTION REPORT', title_format)
                worksheet.merge_range('A2:Z2',
                                      f"Date Range: {context.get('from_date')} to {context.get('to_date')}",
                                      workbook.add_format({'align': 'center', 'italic': True}))

                # Format headers
                for col_num, value in enumerate(columns):
                    worksheet.write(3, col_num, value, header_format)

                # Format data cells
                for row_num in range(4, len(data_rows) + 4):
                    for col_num in range(len(columns)):
                        cell_value = data_rows[row_num - 4][col_num]

                        if row_num == len(data_rows) + 3:  # Grand total row
                            if col_num >= 8:
                                worksheet.write(row_num, col_num, cell_value, total_format)
                            else:
                                worksheet.write(row_num, col_num, cell_value, header_format)
                        else:
                            if col_num in [0, 2, 3, 4, 5, 6, 7]:
                                worksheet.write(row_num, col_num, cell_value, center_format)
                            elif col_num >= 8:
                                worksheet.write(row_num, col_num, cell_value, currency_format)
                            else:
                                worksheet.write(row_num, col_num, cell_value, workbook.add_format(thin_border))

                # Set column widths
                for i, col in enumerate(columns):
                    max_len = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col)) + 2
                    )
                    worksheet.set_column(i, i, max_len + 2)

                worksheet.freeze_panes(4, 2)
                worksheet.set_zoom(90)
                worksheet.autofilter(3, 0, 3, len(columns) - 1)
                worksheet.set_landscape()
                worksheet.set_margins(left=0.5, right=0.5, top=0.75, bottom=0.75)
                worksheet.repeat_rows(0, 3)
                worksheet.print_area(0, 0, len(data_rows) + 3, len(columns) - 1)

            output.seek(0)
            file_path = os.path.join('reports', params["filename"])
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            with open(full_path, 'wb') as f:
                f.write(output.getvalue())

            return file_path

        except Exception as e:
            print(f"Excel Generation Error: {str(e)}")
            raise

# # crucial/tasks.py
# from celery import shared_task
# from django_tenants.utils import schema_context, get_tenant_model
# from django.conf import settings
# import time

# @shared_task
# def generate_head_pdf_report_task(params):
#     try:
#         TenantModel = get_tenant_model()
#         tenant = TenantModel.objects.get(schema_name=params['schema_name'])
        
#         with schema_context(tenant.schema_name):
#             from django.template.loader import render_to_string
#             from weasyprint import HTML
#             from .views import generate_head_report_context
#             from django.test import RequestFactory
#             import os
            
#             factory = RequestFactory()
#             request = factory.get('/dummy-path', params)
#             request.tenant = tenant
            
#             context = generate_head_report_context(request)
#             context['selected_head'] = context['selected_head']  # Already set in context
            
#             html = render_to_string(params['template'], context)
#             pdf = HTML(string=html).write_pdf()
            
#             file_path = os.path.join('reports', params["filename"])
#             full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb') as f:
#                 f.write(pdf)
            
#             return file_path
#     except Exception as e:
#         logger.error(f"PDF Generation Error: {str(e)}")
#         raise


# @shared_task
# def generate_head_excel_report_task(params):
#     try:
#         TenantModel = get_tenant_model()
#         tenant = TenantModel.objects.get(schema_name=params['schema_name'])
        
#         with schema_context(tenant.schema_name):
#             from .views import generate_head_report_context
#             from django.test import RequestFactory
#             import pandas as pd
#             from io import BytesIO
#             import os
            
#             factory = RequestFactory()
#             request = factory.get('/dummy-path', params)
#             request.tenant = tenant
            
#             context = generate_head_report_context(request)
#             students_data = context.get('students_data', [])
#             grand_total = context.get('grand_total', 0)
            
#             # Create DataFrame safely
#             data = []
#             for idx, student in enumerate(students_data):
#                 data.append({
#                     'SL NO': idx + 1,
#                     'Student': student['student'].student_field.name,
#                     'Roll No': student['roll_no'],
#                     'Class': student['class'],
#                     'Group': student['group'],
#                     'Section': student['section'],
#                     'Shift': student['shift'],
#                     'Version': student['version'],
#                     'Amount': float(student['amount'])
#                 })
            
#             df = pd.DataFrame(data)
            
#             output = BytesIO()
#             with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                 df.to_excel(writer, sheet_name='Report', index=False)
#                 worksheet = writer.sheets['Report']
#                 worksheet.write(len(df)+1, 6, 'Grand Total')
#                 worksheet.write(len(df)+1, 7, float(grand_total))
            
#             output.seek(0)
#             file_path = os.path.join('reports', params["filename"])
#             full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb') as f:
#                 f.write(output.getvalue())
            
#             return file_path
#     except Exception as e:
#         logger.error(f"Excel Generation Error: {str(e)}")
#         raise
    
    

