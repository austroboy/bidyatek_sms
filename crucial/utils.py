
from django.apps import apps
from django.http import HttpRequest
from .models import *  # Import your models here
from miscellaneous.models import Institute
# from core.models import *
# from accounting.models import Receive
# from user.models import *

from decimal import Decimal
from collections import defaultdict
# utils.py (update imports section)
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from django.core.paginator import Paginator





# Get models using the apps registry
Receive = apps.get_model('accounting', 'Receive')
StudentClass = apps.get_model('core', 'StudentClass')
StudentSection = apps.get_model('core', 'StudentSection')
StuGroup = apps.get_model('core', 'StuGroup')
StudentShift = apps.get_model('core', 'StudentShift')
StudentProfile = apps.get_model('user','StudentProfile')

ABBREVIATIONS = {
    # Groups
    'Science': 'Sc',
    'Humanities': 'Hum',
    'Business Studies': 'Bst',
    # Shifts
    'Morning': 'M',
    'Day': 'D',
    # Versions
    'English': 'Eng',
    'Bangla': 'Ban'
}

def generate_student_fees_context(request):
    institute = Institute.objects.order_by('-id').first()
    context = {
        'students_data': [],
        'chunks_with_info': [],
        'grand_total': Decimal('0.00'),
        'from_date': None,
        'to_date': None,
        'other_fee_total': Decimal('0.00'),
        'classes': StudentClass.objects.all(),
        'sections': StudentSection.objects.all(),
        'groups': StuGroup.objects.all(),
        'shifts': StudentShift.objects.all(),
        'selected_class': 'All',
        'selected_section': 'All',
        'selected_group': 'All',
        'selected_shift': 'All',
        'selected_version': 'All',
        'institute_logo': request.build_absolute_uri(institute.institute_logo.url) if institute and institute.institute_logo else None
    }
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Validate date parameters
    if not from_date or not to_date:
        missing = []
        if not from_date: missing.append('from_date')
        if not to_date: missing.append('to_date')
        raise ValueError(f"Missing parameters: {', '.join(missing)}")
    
    # if not request.GET.get('from_date') or not request.GET.get('to_date'):
    #     raise ValueError("Both from_date and to_date are required")
    
    # Get selected filters from request
    selected_class_id = request.GET.get('class')
    selected_section_id = request.GET.get('section')
    selected_group_id = request.GET.get('group')
    selected_shift_id = request.GET.get('shift')
    selected_version = request.GET.get('version')

    # Get display names for selected filters
    if selected_class_id:
        try:
            context['selected_class'] = StudentClass.objects.get(id=selected_class_id).name
        except StudentClass.DoesNotExist:
            pass

    if selected_section_id:
        try:
            context['selected_section'] = StudentSection.objects.get(id=selected_section_id).name
        except StudentSection.DoesNotExist:
            pass

    if selected_group_id:
        try:
            context['selected_group'] = ABBREVIATIONS.get(
                StuGroup.objects.get(id=selected_group_id).name.strip(),
                StuGroup.objects.get(id=selected_group_id).name[:3]
            )
        except StuGroup.DoesNotExist:
            pass

    if selected_shift_id:
        try:
            context['selected_shift'] = ABBREVIATIONS.get(
                StudentShift.objects.get(id=selected_shift_id).name.strip(),
                StudentShift.objects.get(id=selected_shift_id).name[:1]
            )
        except StudentShift.DoesNotExist:
            pass

    if selected_version:
        context['selected_version'] = ABBREVIATIONS.get(
            selected_version.strip(),
            selected_version[:3]
        )

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return context

        receives = Receive.objects.filter(
            date__gte=from_date_obj,
            date__lte=to_date_obj,
        ).exclude(voucher_no__startswith='FEE').select_related('student').order_by('student__student_field__name')

        # Apply additional filters from the request
        filters = {
            'student__class_id__class_group_id__class_id': request.GET.get('class'),
            'student__class_id__section_id': request.GET.get('section'),
            'student__class_id__class_group_id__group_id': request.GET.get('group'),
            'student__class_id__shift_id': request.GET.get('shift'),
            'student__version': request.GET.get('version'),
        }
        filters = {k: v for k, v in filters.items() if v}
        receives = receives.filter(**filters)

        # Calculate Other Fee total for entries without students and REC2 vouchers
        other_fee_total = Decimal('0.00')
        student_receives = []

        for receive in receives:
            if receive.voucher_no.startswith('REC2') or not receive.student:
                other_fee_total += receive.amount
            else:
                student_receives.append(receive)

        student_ids = [receive.student_id for receive in student_receives if receive.student_id]
        receive_dates = {receive.created_at.date() for receive in student_receives}

        fees_entries = Fees.objects.filter(
            student_id__in=student_ids,
            updated_at__date__in=receive_dates
        ).select_related('feetype_id__fees_type__fee_head').order_by('id')

        fees_grouped = defaultdict(list)
        for fee in fees_entries:
            key = (fee.student_id_id, fee.updated_at.date(), fee.amount)
            if fee.feetype_id:
                fees_grouped[key].append({
                    'feetype': fee.feetype_id,
                    'fee_id': fee.id
                })

        students_data = defaultdict(lambda: {
            'student': None,
            'payments': defaultdict(Decimal),
            'total': Decimal('0.00'),
            'class': '',
            'group': '',
            'section': '',
            'shift': '',
            'version': ''
        })

        column_totals = defaultdict(Decimal)
        grand_total = Decimal('0.00')
        used_fees = set()

        for receive in student_receives:
            student = receive.student
            key = (student.id, receive.created_at.date(), receive.amount)
            fee_type = None

            possible_fees = fees_grouped.get(key, [])
            for fee_entry in possible_fees:
                if fee_entry['fee_id'] not in used_fees:
                    fee_type = fee_entry['feetype']
                    used_fees.add(fee_entry['fee_id'])
                    break

            if fee_type:
                fee_head = fee_type.fees_type.fee_head
                students_data[student.id]['student'] = student
                students_data[student.id]['payments'][fee_head.id] += receive.amount
                students_data[student.id]['total'] += receive.amount

                # Populate class details with abbreviations
                class_config = student.class_id
                if class_config:
                    class_group = class_config.class_group_id
                    students_data[student.id]['class'] = class_group.class_id.name if class_group else ''
                    
                    # Group abbreviation
                    group_name = class_group.group_id.name if class_group and class_group.group_id else ''
                    students_data[student.id]['group'] = ABBREVIATIONS.get(
                        group_name.strip(), 
                        group_name[:3] if group_name else ''
                    )
                    
                    # Section
                    students_data[student.id]['section'] = class_config.section_id.name if class_config.section_id else ''
                    
                    # Shift abbreviation
                    shift_name = class_config.shift_id.name if class_config.shift_id else ''
                    students_data[student.id]['shift'] = ABBREVIATIONS.get(
                        shift_name.strip(),
                        shift_name[:1] if shift_name else ''
                    )
                
                # Version abbreviation
                version = student.version or ''
                students_data[student.id]['version'] = ABBREVIATIONS.get(
                    version.strip(),
                    version[:3]
                )

                # Update totals
                column_totals[fee_head.id] += receive.amount
                grand_total += receive.amount

        grand_total += other_fee_total

        used_fee_heads = FeeHead.objects.filter(id__in=column_totals.keys()).order_by('name')

        students_list = []
        for student_id, data in students_data.items():
            student = data['student']
            payments = [data['payments'].get(fh.id, Decimal('0.00')) for fh in used_fee_heads]
            students_list.append({
                'student': student,
                'payments': payments,
                'total': data['total'],
                'class': data['class'],
                'group': data['group'],
                'section': data['section'],
                'shift': data['shift'],
                'version': data['version']
            })

        max_columns_per_page = 10
        fee_head_chunks = [list(used_fee_heads)[i:i+max_columns_per_page] 
                          for i in range(0, len(used_fee_heads), max_columns_per_page)]

        for student in students_list:
            student['payment_chunks'] = []
            for chunk in fee_head_chunks:
                chunk_payments = [student['payments'][i] for i, fh in enumerate(used_fee_heads) if fh in chunk]
                student['payment_chunks'].append(chunk_payments)
        
        chunks_with_info = []
        for idx, chunk in enumerate(fee_head_chunks):
            chunk_totals = {fh.id: column_totals[fh.id] for fh in chunk}
            student_payments_for_chunk = []
            for student in students_list:
                payment_chunk = student['payment_chunks'][idx]
                student_payments_for_chunk.append({
                    'student': student['student'],
                    'payments': payment_chunk,
                    'total': student['total'],
                    'class': student['class'],
                    'group': student['group'],
                    'section': student['section'],
                    'shift': student['shift'],
                    'version': student['version'],
                })
            chunks_with_info.append({
                'fee_head_objects': chunk,
                'totals': chunk_totals,
                'chunk_fee_heads': {fh.id: fh.name for fh in chunk},
                'student_payments': student_payments_for_chunk,
            })
            
        page = request.GET.get('page', 1)
        paginator = Paginator(students_list, 100)  # 100 items per page
        
        try:
            students_list = paginator.page(page)
        except PageNotAnInteger:
            students_list = paginator.page(1)
        except EmptyPage:
            students_list = paginator.page(paginator.num_pages)
        
        if 'for_report' not in request.GET:
            page = request.GET.get('page', 1)
            paginator = Paginator(students_list, 100)
            try:
                students_list = paginator.page(page)
            except PageNotAnInteger:
                students_list = paginator.page(1)
            except EmptyPage:
                students_list = paginator.page(paginator.num_pages)

        context.update({
            'students_data': students_list,
            'chunks_with_info': chunks_with_info,
            'all_fee_heads': {fh.id: fh.name for fh in used_fee_heads},
            'used_fee_heads': used_fee_heads, 
            'column_totals': column_totals,
            'grand_total': grand_total,
            'other_fee_total': other_fee_total,
            'from_date': from_date,
            'to_date': to_date
        })

    return context



