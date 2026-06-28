from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import StudentAttendance, StudentProfile, StaffAttendance, StaffAttendanceLog, StaffProfile,  LeaveRequest
from .serializers import StudentAttendanceSerializer, StaffAttendanceSerializer, StaffAttendanceLogSerializer, LeaveRequestSerializer
from datetime import datetime


class StudentMonthlyAttendanceView(APIView):
    def get(self, request, student_id, year, month):
        try:
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                return Response({'error': 'Invalid month'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid year or month format'}, status=status.HTTP_400_BAD_REQUEST)

        student = get_object_or_404(StudentProfile, id=student_id)

        attendances = StudentAttendance.objects.filter(
            name=student,
            attendance_date__year=year,
            attendance_date__month=month
        )

        serializer = StudentAttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StaffMonthlyAttendanceView(APIView):

    def get(self, request, staff_id, year, month):
        try:
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                return Response({'error': 'Invalid month'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid year or month format'}, status=status.HTTP_400_BAD_REQUEST)

        staff = get_object_or_404(StaffProfile, id=staff_id)

        attendances = StaffAttendance.objects.filter(
            name=staff,
            attendance_date__year=year,
            attendance_date__month=month
        )

        serializer = StaffAttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StaffAttendanceLogView(APIView):

    def get(self, request, staff_id):
        staff_attendance_logs = StaffAttendanceLog.objects.filter(staff_attendance__name__id=staff_id)
        serializer = StaffAttendanceLogSerializer(staff_attendance_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StaffAttendanceCreateView(APIView):


    def post(self, request):
        serializer = StaffAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffAttendanceUpdateView(APIView):

    def put(self, request, attendance_id):
        attendance = get_object_or_404(StaffAttendance, id=attendance_id)
        serializer = StaffAttendanceSerializer(attendance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffAttendanceReportView(APIView):

    def get(self, request, year, month):
        try:
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                return Response({'error': 'Invalid month'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid year or month format'}, status=status.HTTP_400_BAD_REQUEST)

        attendance_records = StaffAttendance.objects.filter(
            attendance_date__year=year,
            attendance_date__month=month
        )

        serializer = StaffAttendanceSerializer(attendance_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AddLeaveRequestView(APIView):
    """
    API to create a new leave request.
    """

    def post(self, request):
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({"message": "Leave request added successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditLeaveRequestView(APIView):
    """
    API to update an existing leave request.
    """

    def put(self, request, pk):
        leave_request = get_object_or_404(LeaveRequest, pk=pk)
        serializer = LeaveRequestSerializer(leave_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({"message": "Leave request updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteLeaveRequestView(APIView):
    """
    API to delete a leave request.
    """

    def delete(self, request, pk):
        leave_request = get_object_or_404(LeaveRequest, pk=pk)
        leave_request.delete()
        return Response({"message": "Leave request deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
