from rest_framework import serializers
from .models import (
    Admission_Year, AcademicSession, StudentClass, Subject, 
    StudentSection, StudentShift, StuGroup, Period, 
    ClassGroupConfig, ClassConfig, PeriodConfig, SubjectAssign, 
    SubjectConfig, Mark_type, Mark_config
)

class AdmissionYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission_Year
        fields = '__all__'

class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSession
        fields = '__all__'

class StudentClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class StudentSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSection
        fields = '__all__'

class StudentShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentShift
        fields = '__all__'

class StuGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StuGroup
        fields = '__all__'

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = '__all__'

class ClassGroupConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroupConfig
        fields = '__all__'

class ClassConfigSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_group_id.class_id.name', read_only=True)
    group_name = serializers.CharField(source='class_group_id.group_id.name', read_only=True)
    section_name = serializers.CharField(source='section_id.name', read_only=True)
    shift_name = serializers.CharField(source='shift_id.name', read_only=True)

    class Meta:
        model = ClassConfig
        fields = [
            'id', 'class_name', 'group_name', 'section_name', 'shift_name'
        ]

class PeriodConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodConfig
        fields = '__all__'

class SubjectAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAssign
        fields = '__all__'

class SubjectConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectConfig
        fields = '__all__'

class MarkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark_type
        fields = '__all__'

class MarkConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark_config
        fields = '__all__'
