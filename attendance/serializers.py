from rest_framework import serializers
from .models import StudentAttendance, StaffAttendance, StaffAttendanceLog, LeaveRequest

class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = '__all__' 


class StaffAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAttendance
        fields = '__all__'

class StaffAttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAttendanceLog
        fields = '__all__'
        
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
