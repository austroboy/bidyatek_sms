from django.db import models
from user.models import CustomUser
from django.contrib.auth.models import BaseUserManager

# Custom Managers for Each Role

class StaffManager(BaseUserManager):
    def get_queryset(self, role=None):
        queryset = super(StaffManager, self).get_queryset()
        if role:
            return queryset.filter(groups__name=role)
        return queryset.filter(groups__name='staff')


# class TeacherManager(BaseUserManager):
#     def get_queryset(self):
#         return super(TeacherManager, self).get_queryset().filter(groups__name='teacher')


class ParentManager(BaseUserManager):
    def get_queryset(self):
        return super(ParentManager, self).get_queryset().filter(groups__name='parent')


class StudentManager(BaseUserManager):
    def get_queryset(self):
        return super(StudentManager, self).get_queryset().filter(groups__name='student')

# class AccountManager(BaseUserManager):
#     def get_queryset(self):
#         return super(AccountManager, self).get_queryset().filter(groups__name='account')
    
# class HRManager(BaseUserManager):
#     def get_queryset(self):
#         return super(HRManager, self).get_queryset().filter(groups__name='hr')
    
# class ManagerManager(BaseUserManager):
#     def get_queryset(self):
#         return super(ManagerManager, self).get_queryset().filter(groups__name='manager')
    
# class DataEntryManager(BaseUserManager):
#     def get_queryset(self):
#         return super(DataEntryManager, self).get_queryset().filter(groups__name='dataentry')