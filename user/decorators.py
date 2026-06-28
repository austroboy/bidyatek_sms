from django.http import Http404
from functools import wraps

def is_staff_or_in_group(user, *groups):
    return user.is_staff or user.groups.filter(name__in=groups).exists()

def has_role(user, role_names):
    if hasattr(user, 'staff_profile'):
        return user.staff_profile.role in role_names 
    return False

def is_staff_or_has_role(user, *groups, roles=None):
    return is_staff_or_in_group(user, *groups) or (roles and has_role(user, roles))



# def has_role(user, roles):
#     """Check if the user has one of the allowed roles."""
#     return hasattr(user, 'role') and user.role in roles

# def is_staff_or_in_group(user, groups):
#     """Check if the user is a staff member or belongs to specific groups."""
#     return user.is_staff or user.groups.filter(name__in=groups).exists()

# def role_required(roles=None, groups=None):
#     """Decorator for views requiring specific roles or groups."""
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             if not request.user.is_authenticated:
#                 raise Http404("Not authorized")
#             if (roles and has_role(request.user, roles)) or (groups and is_staff_or_in_group(request.user, groups)):
#                 return view_func(request, *args, **kwargs)
#             raise Http404("Not authorized")
#         return _wrapped_view
#     return decorator

# def staff_or_role_required(groups=None, roles=None):
#     """Decorator for views requiring staff status or specific roles/groups."""
#     return role_required(roles=roles, groups=groups)


# @role_required(roles=['teacher', 'staff'])
# def my_teacher_view(request):
#     return render(request, 'teacher_dashboard.html')

# @role_required(groups=['Admins', 'Managers'])
# def admin_view(request):
#     return render(request, 'admin_dashboard.html')

# @staff_or_role_required(groups=['Admins'], roles=['hr', 'manager'])
# def hr_or_manager_view(request):
#     return render(request, 'hr_manager_dashboard.html')

# Key Features:

#     1.has_role: Checks roles simply.
#     2.is_staff_or_in_group: Combines staff and group membership checks.
#     3.role_required: Core decorator for roles/groups.
#     4.staff_or_role_required: Combines staff, roles, and groups in a single decorator.