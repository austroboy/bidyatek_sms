from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import InstituteSerializer
from .models import *
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .serializers import EventSerializer
# Create your views here.

class InstituteViewSet(viewsets.ModelViewSet):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer

    def create(self, request, *args, **kwargs):
        institute_data = request.data
        institute_logo = request.FILES.get('institute_logo')
        signature = request.FILES.get('signature')

        institute_serializer = InstituteSerializer(data=institute_data)
        institute_serializer.is_valid(raise_exception=True)
        institute = institute_serializer.save()

        if institute_logo:
            institute.institute_logo = institute_logo
            institute.save()

        if signature:
            institute.signature = signature
            institute.save()

        return Response(institute_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        institute_data = request.data
        institute_logo = request.FILES.get('institute_logo')
        signature = request.FILES.get('signature')

        institute_serializer = InstituteSerializer(instance, data=institute_data)
        institute_serializer.is_valid(raise_exception=True)
        institute = institute_serializer.save()

        if institute_logo:
            institute.institute_logo = institute_logo
            institute.save()

        if signature:
            institute.signature = signature
            institute.save()

        return Response(institute_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventListAPIView(GenericAPIView, ListModelMixin):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)