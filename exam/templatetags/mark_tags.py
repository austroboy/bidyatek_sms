from django import template
from django.template.defaultfilters import stringfilter
from exam.models import Graderule
from core.models import SubjectConfig,Subject
from user.models import StudentProfile
register = template.Library()

@register.filter(name='get_letter')
def get_letter(mark):
    mark = float(mark)
    grade_rules = Graderule.objects.filter(min_mark__lte=mark, max_mark__gte=mark).first()
    return grade_rules.grade_name if grade_rules else ""
 
@register.filter(name='get_grade')
def get_grade(mark):
    mark = float(mark)
    grade_rules = Graderule.objects.filter(min_mark__lte=mark, max_mark__gte=mark).first()
    return grade_rules.gpa if grade_rules else "" 

@register.filter
def get_grade_name(gpa):
    grading_rules = Graderule.objects.order_by('-gpa')  # Order by GPA descending
    for rule in grading_rules:
        if gpa >= rule.gpa:
            return rule.grade_name
    return "N/A"


    

@register.filter
def get_subject_mark(class_group_id, subject_name):
    subject_config = SubjectConfig.objects.filter(class_id=class_group_id, subject_id__name=subject_name).first()
    if subject_config:
        return subject_config.mark
    return None

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict) and key in dictionary:
        return dictionary[key]
    return {}



@register.filter
def get_total_marks(mark_dict):
    if isinstance(mark_dict, dict):
        total_marks = sum(mark_data for key, mark_data in mark_dict.items() if key != 'status' and isinstance(mark_data, (int, float)))
        return total_marks
    else:
        return 0
    
@register.filter
def get_status(gpa):
    try:
        gpa = float(gpa)
        if gpa <= 0:
            return 'Failed'
        else:
            return 'Passed'
    except (TypeError, ValueError):
        return 'Invalid'

@register.filter(name='get_subject')
def get_subject(subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        return subject.name
    except Subject.DoesNotExist:
        return "Subject not found"
    

@register.filter(name='get_mark')
def get_mark(mark_dict, mark_type):
    return mark_dict.get(mark_type, '-')

@register.filter
def get_es_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '-')
    return '-'  # Fallback for non-dictionary types

@register.filter
def is_dict(value):
    return isinstance(value, dict)
