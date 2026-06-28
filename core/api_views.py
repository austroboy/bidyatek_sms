from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .models import ClassConfig
from .serializers import *

# List API
class ClassConfigListAPIView(GenericAPIView, ListModelMixin):
    queryset = ClassConfig.objects.all()
    serializer_class = ClassConfigSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AdmissionYearListAPIView(GenericAPIView, ListModelMixin):
    queryset = Admission_Year.objects.all()
    serializer_class = AdmissionYearSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AcademicSessionListAPIView(GenericAPIView, ListModelMixin):
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
