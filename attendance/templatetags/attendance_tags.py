from django import template

register = template.Library()

@register.filter
def get_first_or_none(queryset):
    """
    Custom template filter to return the first element of a queryset,
    or None if the queryset is empty.
    """
    try:
        return queryset.first()
    except AttributeError:
        return None
    
@register.filter
def get_value(d, key):
    return d.get(key, [])