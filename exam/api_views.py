from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import StudentResult, StudentProfile, Admission_Year
from .serializers import StudentResultSerializer

class StudentResultByAcademicYearView(APIView):
    def get(self, request, student_id, academic_year_id):
        student = get_object_or_404(StudentProfile, id=student_id)

        student_results = StudentResult.objects.filter(student=student, academic_year_id=academic_year_id)

        if not student_results.exists():
            return Response({"message": "No results found for this student in the given academic year."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentResultSerializer(student_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
