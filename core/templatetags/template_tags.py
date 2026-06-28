from django import template

register = template.Library()

@register.filter
def modulo(num, val):
    return num % val



@register.filter(name='is_staff_or_in_group')
def is_staff_or_in_group(user, group_names):
    group_list = group_names.split(',')
    return user.is_staff or any(user.groups.filter(name=group_name).exists() for group_name in group_list)



@register.filter(name='in_group')
def in_group(user, group_names):
    group_list = [group.strip() for group in group_names.split(',')]
    return any(user.groups.filter(name=group).exists() for group in group_list)

@register.filter(name='has_role')
def has_role(user, role_name):
    
    if hasattr(user, 'staff_profile'):
        return user.staff_profile.role == role_name
    
    return False

@register.filter
def get_assign_item(dictionary, key):
    return dictionary.get(key)



@register.filter
def get_item(dictionary, key):
    """Return value for a given key from a dictionary"""
    return dictionary.get(key, None)
