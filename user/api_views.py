from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import StudentProfile,StaffProfile
from django.shortcuts import get_object_or_404

class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StudentProfilePagination(PageNumberPagination):
    page_size = 10  # Adjust the page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 100

class StudentProfileListView(generics.ListAPIView):
    serializer_class = StudentProfileSerializer
    pagination_class = StudentProfilePagination
    queryset = StudentProfile.objects.filter(student_field__status="Active")

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['class_id', 'admission_year_id', 'academic_session_year']
    search_fields = ['student_field__name']

class StudentProfileRetrieveAPIView(generics.RetrieveAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    def get(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')  # Get the student ID from URL
        student = get_object_or_404(StudentProfile, id=student_id)  # Fetch student
        serializer = self.get_serializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StaffProfilePagination(PageNumberPagination):
    page_size = 10  # Adjust the page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 100

class StaffProfileListView(generics.ListAPIView):
    serializer_class = StaffProfileSerializer
    pagination_class = StaffProfilePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    def get_queryset(self):
        queryset = StaffProfile.objects.filter(staff_field__status="Active")

        # Get filter type from request
        role_filter = self.request.query_params.get('role_filter')

        if role_filter == "include":  # If "include", filter only Teachers
            queryset = queryset.filter(role__name="Teacher")
        elif role_filter == "exclude":  # If "exclude", exclude Teachers
            queryset = queryset.exclude(role__name="Teacher")

        return queryset
    

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import BasePermission, IsAuthenticated

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()

class StudentProfileView(RetrieveAPIView):
    serializer_class = StudentAppProfileSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_object(self):
        return StudentProfile.objects.get(student_field=self.request.user)