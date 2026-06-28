from django import template
from datetime import datetime

register = template.Library()

@register.filter
def format_date(value):
    formatted_date = value.strftime("%d %B, %Y")
    return formatted_date